""" Module containing the storage services.

Contains the standard :class:`~pypet.storageservice.HDF5StorageSerivce`
as well wrapper classes to allow thread safe multiprocess storing.

"""

__author__ = 'Robert Meyer'


import logging
import tables as pt
import tables.parameters as ptpa
import os
import warnings
import time
import datetime
import Queue
import sys

import numpy as np
from pandas import DataFrame, read_hdf, Series, Panel, Panel4D, HDFStore

from pypet import pypetconstants
import pypet.pypetexceptions as pex
from pypet import __version__ as VERSION
from pypet.parameter import ObjectTable
import pypet.naturalnaming as nn
from pypet.pypetlogging import HasLogger




class MultiprocWrapper(object):
    """Abstract class definition of a Wrapper.

    Note that only storing is required, loading is optional.

    ABSTRACT: Needs to be defined in subclass

    """
    def store(self,*args,**kwargs):
        raise NotImplementedError('Implement this!')


class QueueStorageServiceSender(MultiprocWrapper, HasLogger):
    """ For multiprocessing with :const:`~pypet.pypetconstants.WRAP_MODE_QUEUE`, replaces the
        original storage service.

        All storage requests are send over a queue to the process running the
        :class:`~pypet.storageservice.QueueStorageServiceWriter`.

        Does not support loading of data!

    """
    def __init__(self):
        self.queue = None
        self._set_logger()

    def __setstate__(self, statedict):
        self.__dict__.update(statedict)
        self._set_logger()

    def __getstate__(self):
        result = self.__dict__.copy()
        result['queue'] = None
        del result['_logger']
        return result

    def load(self, *args, **kwargs):
        raise NotImplementedError('Queue wrapping does not support loading. If you want to '
                                  'load data in a multiprocessing environment, use the Lock '
                                  'wrapping.')

    def store(self,*args,**kwargs):
        """Puts data to store on queue."""
        try:
            self.queue.put(('STORE',args,kwargs))
        except IOError:
            ## This is due to a bug in Python, repeating the operation works :-/
            ## See http://bugs.python.org/issue5155
             try:
                self._logger.error('Failed sending task %s to queue, I will try again.' %
                                                str(('STORE',args,kwargs)) )
                self.queue.put(('STORE',args, kwargs))
                self._logger.error('Second queue sending try was successful!')
             except IOError:
                self._logger.error('Failed sending task %s to queue, I will try one last time.' %
                                                str(('STORE',args,kwargs)) )
                self.queue.put(('STORE',args, kwargs))
                self._logger.error('Third queue sending try was successful!')


    def send_done(self):
        """Signals the writer that it can stop listening to the queue"""
        self.queue.put(('DONE',[],{}))

class QueueStorageServiceWriter(object):
    """Wrapper class that listens to the queue and stores queue items via the storage service."""
    def __init__(self, storage_service, queue):
        self._storage_service = storage_service
        self._queue = queue
        self._trajectory_name = None

    def run(self):
        """Starts listening to the queue."""
        while True:
            try:
                to_store_list = []
                stop_listening=False
                while True:
                    # We try to grap more data from the queue to avoid reopneing the
                    # hdf5 file all the time
                    try:
                        msg,args,kwargs = self._queue.get(False)
                        if msg == 'DONE':
                            stop_listening=True
                        elif msg == 'STORE':
                            if 'msg' in kwargs:
                                store_msg = kwargs.pop('msg')
                            else:
                                store_msg = args[0]
                                args = args[1:]
                            if 'stuff_to_store' in kwargs:
                                stuff_to_store = kwargs.pop('stuff_to_store')
                            else:
                                stuff_to_store = args[0]
                                args = args[1:]
                            trajectory_name = kwargs.pop('trajectory_name')
                            if self._trajectory_name is None:
                                self._trajectory_name = trajectory_name
                            elif self._trajectory_name != trajectory_name:
                                raise RuntimeError('Cannot store into two different trajectories. '
                                        'I am supposed to store into %s, but I should also '
                                        'store into %s.' % (self._trajectory_name, trajectory_name))

                            to_store_list.append((store_msg, stuff_to_store, args, kwargs))
                        else:
                            raise RuntimeError('You queued something that was not intended to be queued!')

                    except Queue.Empty:
                        break

                if to_store_list:
                    self._storage_service.store(pypetconstants.LIST, to_store_list,
                                                trajectory_name=self._trajectory_name)
                if stop_listening:
                    break

            except:
                raise
            finally:
                try:
                    self._queue.task_done()
                except ValueError:
                    pass

class LockWrapper(MultiprocWrapper, HasLogger):
    """For multiprocessing in :const:`~pypet.pypetconstants.WRAP_MODE_LOCK` mode,
    augments a storage service with a lock.

    The lock is acquired before storage or loading and released afterwards.

    """
    def __init__(self,storage_service, lock):
        self._storage_service = storage_service
        self._lock = lock
        self._set_logger()

    def store(self,*args, **kwargs):
        """Acquires a lock before storage and releases it afterwards."""
        try:
            self._lock.acquire()
            self._storage_service.store(*args,**kwargs)
        finally:
            if self._lock is not None:
                try:
                    self._lock.release()
                except RuntimeError:
                    self._logger.error('Could not release lock `%s`!' % str(self._lock))

    def load(self,*args,**kwargs):
        """Acquires a lock before loading and releases it afterwards."""
        try:
            self._lock.acquire()
            self._storage_service.load(*args,**kwargs)
        finally:
            if self._lock is not None:
                try:
                    self._lock.release()
                except RuntimeError:
                    self._logger.error('Could not release lock `%s`!' % str(self._lock))


class StorageService(object):
    """Abstract base class defining the storage service interface."""
    def store(self,msg,stuff_to_store,*args,**kwargs):
        """See :class:`pypet.storageservice.HDF5StorageService` for an example of an
        implementation and requirements for the API.

        ABSTRACT: Needs to be defined in subclass

        """
        raise NotImplementedError('Implement this!')

    def load(self,msg,stuff_to_load,*args,**kwargs):
        """ See :class:`pypet.storageservice.HDF5StorageService` for an example of an
        implementation and requirements for the API.

        ABSTRACT: Needs to be defined in subclass

        """
        raise NotImplementedError('Implement this!')


class LazyStorageService(StorageService):
    """This lazy guy does nothing! Only for debugging purposes.

    Ignores all storage and loading requests and simply executes `pass` instead.

    """
    def load(self,*args,**kwargs):
        """Nope, I won't care, dude!"""
        pass

    def store(self,*args,**kwargs):
        """Do whatever you want, I won't store anything!"""
        pass


class NodeProcessingTimer(HasLogger):
    """Simple Class to display the processing of nodes"""
    def __init__(self, display_time=30, logger_name=None):
        self._start_time = time.time()
        self._last_time = self._start_time
        self._display_time = display_time
        self._set_logger(logger_name)
        self._updates=0
        self._last_updates=0

    def signal_update(self):
        """Signals the process timer.

        If more time than the display time has passed a message is emitted.

        """
        self._updates+=1
        current_time = time.time()
        dt = current_time - self._last_time
        if dt > self._display_time:
            dfullt = current_time-self._start_time
            seconds = int(dfullt)%60
            minutes = int(dfullt)/60
            if minutes == 0:
                formatted_time = '%ds' % seconds
            else:
                formatted_time = '%dm%02ds' %(minutes, seconds)
            nodespersecond = self._updates/dfullt
            message = 'Processed %d nodes in %s (%.2f nodes/s).' % \
                      (self._updates, formatted_time, nodespersecond)
            self._logger.info(message)
            self._last_time=current_time


class PTItemMock(object):
    """Class that mocks a PyTables item and wraps around a dictionary"""
    def __init__(self, dictionary):
        self._v_attrs = dictionary

    def _f_setattr(self, name, val):
        self._v_attrs[name]=val


class HDF5StorageService(StorageService, HasLogger):
    """Storage Service to handle the storage of a trajectory/parameters/results into hdf5 files.

    Normally you do not interact with the storage service directly but via the trajectory,
    see :func:`pypet.trajectory.Trajectory.f_store` and :func:`pypet.trajectory.Trajectory.f_load`.

    The service is not thread safe. For multiprocessing the service needs to be wrapped either
    by the :class:`~pypet.storageservice.LockWrapper` or with a combination of
    :class:`~pypet.storageservice.QueueStorageServiceSender` and
    :class:`~pypet.storageservice.QueueStorageServiceWriter`.

    The storage service supports two operations *store* and *load*.

    Requests for these two are always passed as
    `msg, what_to_store_or_load, *args, **kwargs`

    For example:

    >>> HDF5StorageService.load(pypetconstants.LEAF, myresult, load_only=['spikestimes','nspikes'])

    For a list of supported items see :func:`~pypet.storageservice.HDF5StorageService.store`
    and :func:`~pypet.storageservice.HDF5StorageService.load`.

    """

    ADD_ROW = 'ADD'
    ''' Adds a row to an overview table'''
    REMOVE_ROW = 'REMOVE'
    ''' Removes a row from an overview table'''
    MODIFY_ROW = 'MODIFY'
    ''' Changes a row of an overview table'''


    COLL_TYPE ='COLL_TYPE'
    '''Type of a container stored to hdf5, like list,tuple,dict,etc

    Must be stored in order to allow perfect reconstructions.
    '''

    COLL_LIST = 'COLL_LIST'
    ''' Container was a list'''
    COLL_TUPLE = 'COLL_TUPLE'
    ''' Container was a tuple'''
    COLL_NDARRAY = 'COLL_NDARRAY'
    ''' Container was a numpy array'''
    COLL_MATRIX = 'COLL_MATRIX'
    ''' Container was a numpy matrix'''
    COLL_DICT = 'COLL_DICT'
    ''' Container was a dictionary'''
    COLL_SCALAR = 'COLL_SCALAR'
    ''' No container, but the thing to store was a scalar'''

    SCALAR_TYPE = 'SCALAR_TYPE'
    ''' Type of scalars stored into a container'''


    ### Overview Table constants
    CONFIG = 'config'
    PARAMETERS = 'parameters'
    RESULTS = 'results'
    EXPLORED_PARAMETERS = 'explored_parameters'
    DERIVED_PARAMETERS = 'derived_parameters'


    NAME_TABLE_MAPPING ={
           '_overview_config' : 'config',
           '_overview_parameters': 'parameters',
           '_overview_derived_parameters_trajectory' : 'derived_parameters_trajectory',
           '_overview_derived_parameters_runs' : 'derived_parameters_runs',
           '_overview_results_trajectory' : 'results_trajectory',
           '_overview_results_runs': 'results_runs',
           '_overview_explored_parameters': 'explored_parameters',
           '_overview_derived_parameters_runs_summary' : 'derived_parameters_runs_summary',
           '_overview_results_runs_summary' : 'results_runs_summary'
    }
    ''' Mapping of trajectory config names to the tables'''

    PR_ATTR_NAME_MAPPING = {
        '_derived_parameters_per_run' : 'derived_parameters_per_run',
        '_results_per_run' : 'results_per_run',
        '_purge_duplicate_comments' : 'purge_duplicate_comments',
        '_overview_explored_parameters_runs' : 'explored_parameters_runs'
    }
    '''Mapping of Attribute names for hdf5_settings table'''

    ATTR_LIST = [
            'complevel',
            'complib',
            'shuffle',
            'fletcher32',
            'pandas_format',
            'pandas_append'
    ]
    '''List of HDF5StorageService Attributes that have to be stored into the hdf5_settings table'''



    ### Storing Data Constants
    STORAGE_TYPE= 'SRVC_STORE'
    '''Flag, how data was stored'''

    ARRAY = 'ARRAY'
    '''Stored as array_

    .. _array: http://pytables.github.io/usersguide/libref/homogenous_storage.html#the-array-class

    '''
    CARRAY = 'CARRAY'
    '''Stored as carray_

    .. _carray: http://pytables.github.io/usersguide/libref/homogenous_storage.html#the-carray-class

    '''
    EARRAY = 'EARRAY' # not supported yet
    ''' Stored as earray_

    Not supported yet, maybe in near future.

    .. _earray: http://pytables.github.io/usersguide/libref/homogenous_storage.html#the-earray-class

    '''
    VLARRAY = 'VLARRAY' # not supported yet
    '''Stored as vlarray_

    Not supported yet, maybe in near future.

    .. _vlarray: http://pytables.github.io/usersguide/libref/homogenous_storage.html#the-vlarray-class

    '''
    DICT = 'DICT'
    ''' Stored as dict.

    In fact, stored as pytable, but the dictionary wil be reconstructed.
    '''

    TABLE = 'TABLE'
    '''Stored as pytable_

    .. _pytable: http://pytables.github.io/usersguide/libref/structured_storage.html#the-table-class

    '''
    FRAME = 'FRAME'
    ''' Stored as pandas DataFrame_

    .. _DataFrame: http://pandas.pydata.org/pandas-docs/dev/io.html#hdf5-pytables

    '''

    SERIES = 'SERIES'
    ''' Store data as pandas Series '''

    PANEL = 'PANEL'
    ''' Store data as pandas Panel(4D) '''

    SPLIT_TABLE = 'SPLIT_TABLE'
    ''' If a table was split due to too many columns'''

    DATATYPE_TABLE = 'DATATYPE_TABLE'
    '''If a table contains the data types instead of the attrs'''


    TYPE_FLAG_MAPPING = {

        ObjectTable : TABLE,
        list:ARRAY,
        tuple:ARRAY,
        dict: DICT,
        np.ndarray:CARRAY,
        np.matrix:CARRAY,
        DataFrame : FRAME,
        Series : SERIES,
        Panel : PANEL,
        Panel4D : PANEL
    }
    ''' Mapping from object type to storage flag'''

    # Python native data should alwys be stored as an ARRAY
    for item in pypetconstants.PARAMETER_SUPPORTED_DATA:
        TYPE_FLAG_MAPPING[item]=ARRAY


    FORMATTED_COLUMN_PREFIX = 'SRVC_COLUMN_%s_'
    ''' Stores data type of a specific pytables column for perfect reconstruction'''
    DATA_PREFIX = 'SRVC_DATA_'
    ''' Stores data type of a pytables carray or array for perfect reconstruction'''

    # ANNOTATION CONSTANTS
    ANNOTATION_PREFIX = 'SRVC_AN_'
    ''' Prefix to store annotations as node attributes_

    .. _attributes: http://pytables.github.io/usersguide/libref/declarative_classes.html#the-attributeset-class

    '''
    ANNOTATED ='SRVC_ANNOTATED'
    ''' Whether an item was annotated'''


    # Stuff necessary to construct parameters and result
    INIT_PREFIX = 'SRVC_INIT_'
    ''' Hdf5 attribute prefix to store class name of parameter or result'''
    CLASS_NAME = INIT_PREFIX+'CLASS_NAME'
    ''' Name of a parameter or result class, is converted to a constructor'''
    COMMENT = INIT_PREFIX+'COMMENT'
    ''' Comment of parameter or result'''
    LENGTH = INIT_PREFIX+'LENGTH'
    ''' Length of a parameter if it is explored'''
    LEAF = 'SRVC_LEAF'
    ''' Whether an hdf5 node is a leaf node'''


    def __init__(self, filename=None, file_title='Experiment', display_time=30):
        self._filename = filename
        self._file_title = file_title
        self._trajectory_name = None
        self._trajectory_index = None
        self._hdf5file = None
        self._hdf5store = None
        self._trajectory_group = None # link to the top group in hdf5 file which is the start
        # node of a trajectory
         # remembers whether to purge duplicate comments
        self._set_logger()
        self._complevel = 9
        self._complib = 'zlib'
        self._fletcher32 = False
        self._shuffle = True

        self._node_processing_timer = None

        self._display_time = display_time

        self._pandas_append = False
        self._pandas_format = 'fixed'

        self._purge_duplicate_comments = False
        self._results_per_run = False
        self._derived_parameters_per_run = False

        self._overview_parameters = False
        self._overview_config = False
        self._overview_explored_parameters = False
        self._overview_explored_parameters_runs = False
        self._overview_derived_parameters_trajectory = False
        self._overview_derived_parameters_runs = False
        self._overview_derived_parameters_runs_summary = False
        self._overview_results_trajectory = False
        self._overview_results_runs = False
        self._overview_results_runs_summary = False



        # We don't want the NN warnings of pytables to display because they can be
        # annoying as hell
        warnings.simplefilter('ignore', pt.NaturalNameWarning)

    @property
    def display_time(self):
        """Time interval in seconds, when to display the storage or loading of nodes"""
        return self._display_time

    @display_time.setter
    def display_time(self, display_time):
        self._display_time = display_time

    @property
    def complib(self):
        "Compression library used"
        return self._complib

    @complib.setter
    def complib(self, complib):
        self._complib = complib
        self._filters=None

    @property
    def complevel(self):
        """Compression level used"""
        return self._complevel

    @complevel.setter
    def complevel(self, complevel):
        self._complevel = complevel
        self._filters=None


    @property
    def fletcher32(self):
        """ Whether fletcher 32 should be used """
        return self._fletcher32

    @fletcher32.setter
    def fletcher32(self, fletcher32):
        self._fletcher32 = bool(fletcher32)
        self._filters=None

    @property
    def shuffle(self):
        """ Whether shuffle filtering should be used"""
        return self._shuffle

    @shuffle.setter
    def shuffle(self, shuffle):
        self._shuffle = bool(shuffle)
        self._filters=None

    @property
    def pandas_append(self):
        """ If pandas should create storage in append mode"""
        return self._pandas_append

    @pandas_append.setter
    def pandas_append(self, pandas_append):
        self._pandas_append = bool(pandas_append)

    @property
    def pandas_format(self):
        """Format of pandas data. Applicable formats are 'table' (or 't') and 'fixed' (or 'f')"""
        return self._pandas_format

    @pandas_format.setter
    def pandas_format(self, pandas_format):
        if pandas_format not in ('f', 'fixed', 'table', 't'):
            raise ValueError('''Pandas format can only be 'table' (or 't') and 'fixed' (or 'f')
                            not `%s`.''' % pandas_format)
        self._pandas_format = pandas_format


    @property
    def filename(self):
        """The name and path of the underlying hdf5 file."""
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename


    @property
    def _overview_group(self):
        """Direct link to the overview group"""
        return self._all_create_or_get_groups('overview')[0]

    def _get_filters(self):
        """Makes filter and closes pandas store"""
        if self._filters is None:
            self._filters = pt.Filters(complib=self._complib, complevel=self._complevel,
                                       shuffle=self._shuffle, fletcher32=self._fletcher32)
            self._hdf5store._filters=self._filters
            self._hdf5store._complevel = self._complevel
            self._hdf5store._complib=self._complib
            self._hdf5store._fletcher32 = self._fletcher32

        return self._filters


    def load(self,msg,stuff_to_load,*args,**kwargs):
        """Loads a particular item from disk.

        The storage service always accepts these parameters:

        :param trajectory_name: Name of current trajectory and name of top node in hdf5 file.

        :param trajectory_index:

            If no `trajectory_name` is provided, you can specify an integer index.
            The trajectory at the index position in the hdf5 file is considered to loaded.
            Negative indices are also possible for reverse indexing.

        :param filename: Name of the hdf5 file


        The following messages (first argument msg) are understood and the following arguments
        can be provided in combination with the message:

            * :const:`pypet.pypetconstants.TRAJECTORY` ('TRAJECTORY')

                Loads a trajectory.

                :param stuff_to_load: The trajectory

                :param as_new: Whether to load trajectory as new

                :param load_parameters: How to load parameters and config

                :param load_derived_parameters: How to load derived parameters

                :param load_results: How to load results

                :param force: Force load in case there is a pypet version mismatch

                You can specify how to load the parameters, derived parameters and results
                as follows:

                 :const:`pypet.pypetconstants.LOAD_NOTHING`: (0)

                    Nothing is loaded

                :const:`pypet.pypetconstants.LOAD_SKELETON`: (1)

                    The skeleton including annotations are loaded, i.e. the items are empty.
                    Non-empty items in RAM are left untouched.

                :const:`pypet.pypetconstants.LOAD_DATA`: (2)

                    The whole data is loaded.
                    Only empty or in RAM non-existing instance are filled with the
                    data found on disk.

                :const:`pypet.pypetconstants.OVERWRITE_DATA`: (3)

                    The whole data is loaded.
                    If items that are to be loaded are already in RAM and not empty,
                    they are emptied and new data is loaded from disk.

            * :const:`pypet.pypetconstants.LEAF` ('LEAF')

                Loads a parameter or result.

                :param stuff_to_load: The item to be loaded

                :param load_only:

                    If you load a result, you can partially load it and ignore the rest of the data.
                    Just specify the name of the data you want to load. You can also provide a list,
                    for example `load_only='spikes'`, `load_only=['spikes','membrane_potential']`.

                    Issues a warning if items cannot be found.

                :param load_except:

                    If you load a result you can partially load in and specify items
                    that should NOT be loaded here. You cannot use `load_except` and
                    `load_only` at the same time.

            * :const:`pypet.pypetconstants.TREE` ('TREE')

                Loads a whole subtree

                :param stuff_to_load: The parent node (!) not the one where loading starts!

                :param child_name: Name of child node that should be loaded

                :param recursive: Whether to load recursively the subtree below child

                :param load_data:

                    How to load stuff, accepted values as above for loading the trajectory

                :param trajectory: The trajectory object

            * :const:`pypet.pypetconstants.LIST` ('LIST')

                Analogous to :ref:`storing lists <store-lists>`

        :raises:

            NoSuchServiceError if message or data is not understood

            DataNotInStorageError if data to be loaded cannot be found on disk

        """
        opened = True
        try:

            self._srvc_extract_file_information(kwargs)

            args = list(args)

            opened = self._srvc_opening_routine('r')

            if msg == pypetconstants.TRAJECTORY:
                self._trj_load_trajectory(msg,stuff_to_load,*args,**kwargs)

            elif msg == pypetconstants.LEAF:
                self._prm_load_parameter_or_result(stuff_to_load,*args,**kwargs)

            elif msg == pypetconstants.TREE:
                self._tree_load_tree(stuff_to_load,*args,**kwargs)

            elif msg ==pypetconstants.LIST:
                self._srvc_load_several_items(stuff_to_load,*args,**kwargs)

            else:
                raise pex.NoSuchServiceError('I do not know how to handle `%s`' % msg)

            self._srvc_closing_routine(opened)
        except pt.NoSuchNodeError as e:
            self._srvc_closing_routine(opened)
            self._logger.error('Failed loading  `%s`' % str(stuff_to_load))
            raise pex.DataNotInStorageError(e.message)
        except:
            self._srvc_closing_routine(opened)
            self._logger.error('Failed loading  `%s`' % str(stuff_to_load))
            raise

    def store(self, msg, stuff_to_store, *args, **kwargs):
        """ Stores a particular item to disk.

        The storage service always accepts these parameters:

        :param trajectory_name: Name or current trajectory and name of top node in hdf5 file

        :param filename: Name of the hdf5 file

        :param file_title: If file needs to be created, assigns a title to the file.


        The following messages (first argument msg) are understood and the following arguments
        can be provided in combination with the message:

            * :const:`pypet.pypetconstants.PREPARE_MERGE` ('PREPARE_MERGE'):

                Called to prepare a trajectory for merging, see also 'MERGE' below.

                Will also be called if merging cannot happen within the same hdf5 file.
                Stores already enlarged parameters and updates meta information.

                :param stuff_to_store: Trajectory that is about to be extended by another one

                :param changed_parameters:

                    List containing all parameters that were enlarged due to merging

            * :const:`pypet.pypetconstants.MERGE` ('MERGE')

                Note that before merging within HDF5 file, the storage service will be called
                with msg='PREPARE_MERGE' before, see above.

                Raises a ValueError if the two trajectories are not stored within the very
                same hdf5 file. Then the current trajectory needs to perform the merge slowly
                item by item.

                Merges two trajectories, parameters are:

                :param stuff_to_store: The trajectory data is merged into

                :param other_trajectory_name: Name of the other trajectory

                :param rename_dict:

                    Dictionary containing the old result and derived parameter names in the
                    other trajectory and their new names in the current trajectory.

                :param move_nodes:

                    Whether to move the nodes from the other to the current trajectory

                :param delete_trajectory:

                    Whether to delete the other trajectory after merging.

            * :const:`pypet.pypetconstants.BACKUP` ('BACKUP')

                :param stuff_to_store: Trajectory to be backed up

                :param backup_filename:

                    Name of file where to store the backup. If None the backup file will be in
                    the same folder as your hdf5 file and named 'backup_XXXXX.hdf5'
                    where 'XXXXX' is the name of your current trajectory.

            * :const:`pypet.pypetconstants.TRAJECTORY` ('TRAJECTORY')

                Stores the whole trajectory

                :param stuff_to_store: The trajectory to be stored

                :param only_init:

                    If you just want to initialise the store. If yes, only meta information about
                    the trajectory is stored and none of the nodes/leaves within the trajectory.

            * :const:`pypet.pypetconstants.SINGLE_RUN` ('SINGLE_RUN')

                :param stuff_to_store: The single run to be stored

                :param store_data: If all data belwo `run_XXXXXXXX` should be stored

                :param store_final: If final meta info should be stored

            * :const:`pypet.pypetconstants.LEAF`

                Stores a parameter or result.

                Modification of results is not supported (yet). Everything stored to disk is
                set in stone!

                Note that everything that is supported by the storage service and that is
                stored to disk will be perfectly recovered.
                For instance, you store a tuple of numpy 32 bit integers, you will get a tuple
                of numpy 32 bit integers after loading independent of the platform!

                :param stuff_to_sore: Result or parameter to store

                    In order to determine what to store, the function '_store' of the parameter or
                    result is called. This function returns a dictionary with name keys and data to
                    store as values. In order to determine how to store the data, the storage flags
                    are considered, see below.

                    The function '_store' has to return a dictionary containing values only from
                    the following objects:

                        * python natives (int, long, str, bool, float, complex),

                        *
                            numpy natives, arrays and matrices of type np.int8-64, np.uint8-64,
                            np.float32-64, np.complex, np.str

                        *

                            python lists and tuples of the previous types
                            (python natives + numpy natives and arrays)
                            Lists and tuples are not allowed to be nested and must be
                            homogeneous, i.e. only contain data of one particular type.
                            Only integers, or only floats, etc.

                        *

                            python dictionaries of the previous types (not nested!), data can be
                            heterogeneous, keys must be strings. For example, one key-value-pair
                            of string and int and one key-value pair of string and float, and so
                            on.

                        * pandas DataFrames_

                        * :class:`~pypet.parameter.ObjectTable`

                    .. _DataFrames: http://pandas.pydata.org/pandas-docs/dev/dsintro.html#dataframe

                    The keys from the '_store' dictionaries determine how the data will be named
                    in the hdf5 file.

                :param store_flags: Flags describing how to store data.

                        :const:`~pypet.HDF5StorageService.ARRAY` ('ARRAY')

                            Store stuff as array

                        :const:`~pypet.HDF5StorageService.CARRAY` ('CARRAY')

                            Store stuff as carray

                        :const:`~pypet.HDF5StorageService.TABLE` ('TABLE')

                            Store stuff as pytable

                        :const:`~pypet.HDF5StorageService.DICT` ('DICT')

                            Store stuff as pytable but reconstructs it later as dictionary
                            on loading

                        :const:`~pypet.HDF%StorageService.FRAME` ('FRAME')

                            Store stuff as pandas data frame

                    Storage flags can also be provided by the parameters and results themselves
                    if they implement a function '_store_flags' that returns a dictionary
                    with the names of the data to store as keys and the flags as values.

                    If no storage flags are provided, they are automatically inferred from the
                    data. See :const:`pypet.HDF5StorageService.TYPE_FLAG_MAPPING` for the mapping
                    from type to flag.

                :param overwrite:

                    Can be used if parts of a leaf should be replaced. Either a list of
                    HDF5 names or `True` if this should account for all.

            * :const:`pypet.pypetconstants.DELETE` ('DELETE')

                Removes an item from disk. Empty group nodes, results and non-explored
                parameters can be removed.

                :param stuff_to_store: The item to be removed.

                :param remove_empty_groups:

                    Whether to also remove groups that become empty due to removal.
                    default is False.

                :param delete_only:

                    Potential list of parts of a leaf node that should be deleted.

                :param remove_from_item:

                    If `delete_only` is used, whether deleted nodes should also be erased
                    from the leaf nodes themseleves.

            * :const:`pypet.pypetconstants.GROUP` ('GROUP')

                :param stuff_to_store: The group to store

            * :const:`pypet.pypetconstants.TREE`

                Stores a single node or a full subtree

                :param stuff_to_store: Node to store

                :param recursive: Whether to store recursively the whole sub-tree

            * :const:`pypet.pypetconstants.LIST`

                .. _store-lists:

                Stores several items at once

                :param stuff_to_store:

                    Iterable whose items are to be stored. Iterable must contain tuples,
                    for example `[(msg1,item1,arg1,kwargs1),(msg2,item2,arg2,kwargs2),...]`

        :raises: NoSuchServiceError if message or data is not understood

        """
        opened = True
        try:

            self._srvc_extract_file_information(kwargs)


            args = list(args)


            opened= self._srvc_opening_routine('a',msg)

            if msg == pypetconstants.MERGE:
                self._trj_merge_trajectories(*args,**kwargs)

            elif msg == pypetconstants.BACKUP:
                self._trj_backup_trajectory(stuff_to_store,*args,**kwargs)

            elif msg == pypetconstants.PREPARE_MERGE:
                self._trj_prepare_merge(stuff_to_store,*args,**kwargs)

            elif msg == pypetconstants.TRAJECTORY:
                self._trj_store_trajectory(stuff_to_store, *args, **kwargs)

            elif msg == pypetconstants.SINGLE_RUN:
                self._srn_store_single_run(stuff_to_store,*args,**kwargs)

            elif msg in (pypetconstants.LEAF):
                self._prm_store_parameter_or_result(msg,stuff_to_store,*args,**kwargs)

            elif msg == pypetconstants.DELETE:
                self._all_delete_parameter_or_result_or_group(stuff_to_store,*args,**kwargs)

            elif msg == pypetconstants.GROUP:
                self._grp_store_group(stuff_to_store, *args, **kwargs)

            elif msg == pypetconstants.TREE:
                self._tree_store_tree(stuff_to_store,*args,**kwargs)

            elif msg == pypetconstants.LIST:
                self._srvc_store_several_items(stuff_to_store,*args,**kwargs)

            else:
                raise pex.NoSuchServiceError('I do not know how to handle `%s`' % msg)

            self._srvc_closing_routine(opened)

        except:
            self._srvc_closing_routine(opened)
            self._logger.error('Failed storing `%s`' % str(stuff_to_store))
            raise


    def _srvc_load_several_items(self,iterable,*args,**kwargs):
        """Loads several items from an iterable

        Iterables are supposed to be of a format like `[(msg, item, args, kwarg),...]`
        If `args` and `kwargs` are not part of a tuple, they are taken from the
        current `args` and `kwargs` provided to this function.

        """
        for input_tuple in iterable:
            msg = input_tuple[0]
            item = input_tuple[1]
            if len(input_tuple) > 2:
                args = input_tuple[2]
            if len(input_tuple) > 3:
                kwargs = input_tuple[3]
            if len(input_tuple)> 4:
                raise RuntimeError('You shall not pass!')

            self.load(msg,item,*args,**kwargs)

    def _srvc_check_hdf_properties(self, traj):
        """Reads out the properties for storing new data into the hdf5file

        :param traj:

            The trajectory

        """

        for attr_name in HDF5StorageService.ATTR_LIST:
            try:
                config = traj.f_get('config.hdf5.'+attr_name).f_get()
                setattr(self, attr_name, config)
            except AttributeError:
                self._logger.warning('Could not find `%s` in traj, '
                                     'using default value.' % attr_name)

        for attr_name, table_name in HDF5StorageService.NAME_TABLE_MAPPING.items():
            try:
                config = traj.f_get('config.hdf5.overview.' + table_name).f_get()
                setattr(self, attr_name, config)
            except AttributeError:
                self._logger.warning('Could not find `%s` in traj, '
                                     'using default value.' % table_name)

        for attr_name, name in HDF5StorageService.PR_ATTR_NAME_MAPPING.items():
            try:
                config = traj.f_get('config.hdf5.' + name).f_get()
                setattr(self, attr_name, config)
            except AttributeError:
                self._logger.warning('Could not find `%s` in traj, '
                                     'using default value.' % name)

        self._filters=None




    def _srvc_store_several_items(self, iterable, *args, **kwargs):
        """Stores several items from an iterable

        Iterables are supposed to be of a format like `[(msg, item, args, kwarg),...]`
        If `args` and `kwargs` are not part of a tuple, they are taken from the
        current `args` and `kwargs` provided to this function.

        """
        for input_tuple in iterable:
            msg = input_tuple[0]
            item = input_tuple[1]
            if len(input_tuple) > 2:
                args = input_tuple[2]
            if len(input_tuple) > 3:
                kwargs = input_tuple[3]
            if len(input_tuple)> 4:
                raise RuntimeError('You shall not pass!')

            self.store(msg,item,*args,**kwargs)

    def _srvc_opening_routine(self,mode,msg=None):
        """Opens an hdf5 file for reading or writing

        The file is only opened if it has not been opened before (i.e. `self._hdf5file is None`).

        :param mode:

            'w' for writing

            'a' for appending

            'r' for reading

                Unfortunately, pandas currently does not work with read-only mode.
                Thus, if mode is chosen to be 'r', the file will still be opened in
                append mode.

        :param msg:

            Message provided to `load` or `store`. Only considered to check if a trajectory
            was stored before.

        :return:

            `True` if file is opened

            `False` if the file was already open before calling this function

        """
        self._mode = mode
        if self._hdf5file is None:

            if 'a' in mode or 'w' in mode:
                (path, filename)=os.path.split(self._filename)
                if not os.path.exists(path):
                    os.makedirs(path)

                self._hdf5store = HDFStore(self._filename, self._mode, complib=self._complib,
                                           complevel=self._complevel, fletcher32=self._fletcher32)
                self._hdf5file = self._hdf5store._handle
                self._hdf5file.title = self._file_title

                if not ('/'+self._trajectory_name) in self._hdf5file:
                    # If we want to store individual items we we have to check if the
                    # trajectory has been stored before
                    if not msg == pypetconstants.TRAJECTORY:
                        raise ValueError('Your trajectory cannot be found in the hdf5file, '
                                         'please use >>traj.f_store()<< before storing anyhting else.')

                    # If we want to store a trajectory it has not been stored before
                    # create a new trajectory group
                    try:
                        self._hdf5file.create_group(where='/', name= self._trajectory_name,
                                               title=self._trajectory_name)
                    except AttributeError:
                        self._hdf5file.createGroup(where='/', name= self._trajectory_name,
                                               title=self._trajectory_name)

                # Store a reference to the top trajectory node
                try:
                    self._trajectory_group = self._hdf5file.get_node('/'+self._trajectory_name)
                except AttributeError:
                    self._trajectory_group = self._hdf5file.getNode('/'+self._trajectory_name)

            elif mode == 'r':

                if not self._trajectory_name is None and not self._trajectory_index is None:

                    raise ValueError('Please specify either a name of a trajectory or an index, '
                                 'but not both at the same time.')

                if not os.path.isfile(self._filename):
                    raise ValueError('File `' + self._filename + '` does not exist.')

                self._hdf5store = HDFStore(self._filename, self._mode, complib=self._complib,
                                           complevel=self._complevel, fletcher32=self._fletcher32)
                self._hdf5file = self._hdf5store._handle


                if not self._trajectory_index is None:
                    # If an index is provided pick the trajectory at the corresponding
                    # position in the trajectory node list
                    try:
                        nodelist = self._hdf5file.list_nodes(where='/')
                    except AttributeError:
                        nodelist = self._hdf5file.listNodes(where='/')

                    if (self._trajectory_index >= len(nodelist) or
                                self._trajectory_index  < -len(nodelist)):

                        raise ValueError('Trajectory No. %d does not exists, there are only '
                                         '%d trajectories in %s.'
                                    % (self._trajectory_index,len(nodelist),self._filename))

                    self._trajectory_group = nodelist[self._trajectory_index]
                    self._trajectory_name = self._trajectory_group._v_name

                elif not self._trajectory_name is None:
                    # Otherwise pick the trajectory group by name
                    if not ('/'+self._trajectory_name) in self._hdf5file:
                        raise ValueError('File %s does not contain trajectory %s.'
                                         % (self._filename, self._trajectory_name))

                    try:
                        self._trajectory_group = self._hdf5file.get_node('/'+
                                                                        self._trajectory_name)
                    except AttributeError:
                        self._trajectory_group = self._hdf5file.getNode('/'+
                                                                        self._trajectory_name)
                else:
                    raise ValueError('Please specify a name of a trajectory to load or its '
                                     'index, otherwise I cannot open one.')

            else:
                raise RuntimeError('You shall not pass!')

            self._node_processing_timer=NodeProcessingTimer(display_time=self._display_time,
                        logger_name=self._logger.name)

            return True
        else:
            return False


    def _srvc_closing_routine(self, closing):
        """Routine to close an hdf5 file

        The file is closed only when `closing=True`. `closing=True` means that
        the file was opened in the current highest recursion level. This prevents re-opening
        and closing of the file if `store` or `load` are called recursively.

        """
        if closing and self._hdf5file is not None and self._hdf5file.isopen:
            f_fd = self._hdf5file.fileno()
            self._hdf5file.flush()
            os.fsync(f_fd)
            try:
                self._hdf5store.flush(fsync=True)
            except TypeError:
                f_fd = self._hdf5store._handle.fileno()
                self._hdf5store.flush()
                os.fsync(f_fd)
            self._hdf5store.close()
            self._hdf5store = None
            self._hdf5file = None
            self._trajectory_group = None
            self._trajectory_name = None
            self._trajectory_index=None
            return True
        else:
            return False

    def _srvc_extract_file_information(self,kwargs):
        """Extracts file information from kwargs.

        Note that `kwargs` is not passed as `**kwargs` in order to also
        `pop` the elements on the level of the function calling `_srvc_extract_file_information`.

        """
        if 'filename' in kwargs:
            self._filename=kwargs.pop('filename')

        if 'file_title' in kwargs:
            self._file_title = kwargs.pop('file_title')

        if 'trajectory_name' in kwargs:
            self._trajectory_name = kwargs.pop('trajectory_name')

        if 'trajectory_index' in kwargs:
            self._trajectory_index = kwargs.pop('trajectory_index')



    ########################### MERGING ###########################################################

    def _trj_backup_trajectory(self, traj, backup_filename=None):
        """Backs up a trajectory.

        :param traj: Trajectory that should be backed up

        :param backup_filename:

            Path and filename of backup file. If None is specified the storage service
            defaults to `path_to_trajectory_hdf5_file/backup_trajectory_name.hdf`.

        """
        self._logger.info('Storing backup of %s.' % traj.v_name)

        mypath, filename = os.path.split(self._filename)

        if backup_filename is None:
            backup_filename ='%s/backup_%s.hdf5' % (mypath,traj.v_name)

        try:
            backup_hdf5file = pt.open_file(filename=backup_filename, mode='a', title=backup_filename)
        except AttributeError:
            backup_hdf5file = pt.openFile(filename=backup_filename, mode='a', title=backup_filename)

        if ('/'+self._trajectory_name) in backup_hdf5file:

            raise ValueError('I cannot backup  `%s` into file `%s`, there is already a '
                             'trajectory with that name.' % (traj.v_name,backup_filename))

        backup_root = backup_hdf5file.root

        self._trajectory_group._f_copy(newparent=backup_root, recursive=True)

        backup_hdf5file.flush()
        backup_hdf5file.close()

        self._logger.info('Finished backup of %s.' % traj.v_name)

    def _trj_copy_table_entries(self, rename_dict, other_trajectory_name):
        """Copy the overview table entries from another trajectory into the current one.

        :param rename_dict:

            Dictionary with old names (keys) and new names (values).

        :param other_trajectory_name:

            Name of other trajectory

        """
        self._trj_copy_table_entries_from_table_name('derived_parameters_runs',rename_dict,other_trajectory_name)
        self._trj_copy_table_entries_from_table_name('results_trajectory',rename_dict,other_trajectory_name)
        self._trj_copy_table_entries_from_table_name('results_runs',rename_dict,other_trajectory_name)

        self._trj_copy_summary_table_entries_from_table_name('results_runs_summary', rename_dict, other_trajectory_name)
        self._trj_copy_summary_table_entries_from_table_name('derived_parameters_runs_summary', rename_dict, other_trajectory_name)

    def _trj_copy_summary_table_entries_from_table_name(self, tablename, rename_dict, other_trajectory_name):
        """Copy a the summary table entries from another trajectory into the current one

        :param tablename:

            Name of overview table

        :param rename_dict:

            Dictionary with old names (keys) and new names (values).

        :param other_trajectory_name:

            Name of other trajectory

        """
        count_dict = {} # Dictionary containing the number of items that are merged for
                        # a particular result summary

        for old_name in rename_dict:
            # Check for the summary entry in the other trajectory
            # In the overview table location literally contains `run_XXXXXXXX`
            run_mask = pypetconstants.RUN_NAME+'X'*pypetconstants.FORMAT_ZEROS

            old_split_name = old_name.split('.')
            for idx, name in enumerate(old_split_name):
                add_to_count = False
                if (name.startswith(pypetconstants.RUN_NAME)
                        and name != pypetconstants.RUN_NAME_DUMMY):
                    old_split_name[idx]=run_mask
                    add_to_count = True
                    break

            if add_to_count:
                old_mask_name = '.'.join(old_split_name)

                if not old_mask_name in count_dict:
                    count_dict[old_mask_name]=0

                count_dict[old_mask_name] += 1


        try:
            # get the other table
            try:
                other_table = self._hdf5file.get_node('/'+other_trajectory_name+'/overview/'+tablename)
            except AttributeError:
                other_table = self._hdf5file.getNode('/'+other_trajectory_name+'/overview/'+tablename)

            new_row_dict={} # Dictionary with full names as keys and summary row dicts as values


            for row in other_table:
                # Iterate through the rows of the overview table
                location = row['location']
                name = row['name']
                full_name = location+'.'+name

                # If we need the overview entry mark it for merging
                if full_name in count_dict:
                    new_row_dict[full_name] = self._trj_read_out_row(other_table.colnames, row)

            # Get the summary table in the current trajectory
            try:
                table= self._hdf5file.get_node('/'+self._trajectory_name+'/overview/'+tablename)
            except AttributeError:
                table= self._hdf5file.getNode('/'+self._trajectory_name+'/overview/'+tablename)

            for row in table:
                # Iterate through the current rows
                location = row['location']
                name = row['name']
                full_name = location+'.'+name

                # Update the number of items according to the number or merged items
                if full_name in new_row_dict:
                    row['number_of_items'] = row['number_of_items'] + count_dict[full_name]
                    # Delete used row dicts
                    del new_row_dict[full_name]
                    row.update()

            table.flush()
            self._hdf5file.flush()

            # Finally we need to create new rows for results that are part of the other
            # trajectory but which could not be found in the current one
            for key in sorted(new_row_dict.keys()):
                not_inserted_row = new_row_dict[key]
                new_row = table.row

                for col_name in table.colnames:

                    # This is to allow backwards compatibility
                    if col_name == 'example_item_run_name' and not col_name in other_table.colnames:
                        continue

                    if col_name == 'example_item_run_name':
                        # The example item run name has changed due to merging
                        old_run_idx = not_inserted_row[col_name]
                        old_run_name = pypetconstants.FORMATTED_RUN_NAME % old_run_idx
                        new_run_name = rename_dict[old_run_name]
                        new_run_idx = int(new_run_name.split(pypetconstants.RUN_NAME)[1])
                        new_row[col_name] = new_run_idx
                    else:
                        new_row[col_name] = not_inserted_row[col_name]

                new_row.append()

            table.flush()
            self._hdf5file.flush()

        except pt.NoSuchNodeError:
            self._logger.warning('Did not find table `%s` in one of the trajectories,'
                              ' skipped copying.' % tablename)

    @staticmethod
    def _trj_read_out_row(colnames,row):
        """Reads out a row and returns a dictionary containing the row content.

        :param colnames: List of column names
        :param row:  A pytables table row
        :return: A dictionary with colnames as keys and content as values

        """
        result_dict= {}
        for colname in colnames:
            result_dict[colname]=row[colname]

        return result_dict

    def _trj_copy_table_entries_from_table_name(self,tablename, rename_dict,other_trajectory_name):
        """Copy overview tables (not summary) from other trajectory into the current one.

        :param tablename:

            Name of overview table

        :param rename_dict:

            Dictionary with old names (keys) and new names (values).

        :param other_trajectory_name:

            Name of other trajectory

        """
        try:
            try:
                other_table = self._hdf5file.get_node('/'+other_trajectory_name+'/overview/'+tablename)
            except AttributeError:
                other_table = self._hdf5file.getNode('/'+other_trajectory_name+'/overview/'+tablename)

            new_row_dict={}

            for row in other_table.iterrows():
                # Iterate through the summary table
                location = row['location']
                name = row['name']
                full_name = location+'.'+name


                if full_name in rename_dict:
                    # If the item is marked for merge we need to copy its overview info
                    read_out_row = self._trj_read_out_row(other_table.colnames,row)
                    new_location = rename_dict[full_name].split('.')
                    new_location = '.'.join(new_location[0:-1])
                    read_out_row['location'] = new_location
                    new_row_dict[rename_dict[full_name]] = read_out_row

            try:
                table= self._hdf5file.get_node('/'+self._trajectory_name+'/overview/'+tablename)
            except AttributeError:
                table= self._hdf5file.getNode('/'+self._trajectory_name+'/overview/'+tablename)

            # Insert data into the current overview table
            for row in table.iterrows():
                location = row['location']
                name = row['name']
                full_name = location+'.'+name

                if full_name in new_row_dict:
                    for col_name in table.colnames:
                        row[col_name] = new_row_dict[full_name][col_name]

                    del new_row_dict[full_name]
                    row.update()

            table.flush()
            self._hdf5file.flush()

            # It may be the case that the we need to insert a new row
            for key in sorted(new_row_dict.keys()):
                not_inserted_row = new_row_dict[key]
                new_row = table.row

                for col_name in table.colnames:
                    new_row[col_name] = not_inserted_row[col_name]

                new_row.append()

            table.flush()
            self._hdf5file.flush()

        except pt.NoSuchNodeError:
            self._logger.warning('Did not find table `%s` in one of the trajectories,'
                              ' skipped copying.' % tablename)

    def _trj_merge_trajectories(self,other_trajectory_name,rename_dict,move_nodes=False,
                                delete_trajectory=False):
        """Merges another trajectory into the current trajectory (as in self._trajectory_name).

        :param other_trajectory_name: Name of other trajectory
        :param rename_dict: Dictionary with old names (keys) and new names (values).
        :param move_nodes: Whether to move hdf5 nodes or copy them
        :param delete_trajectory: Whether to delete the other trajectory

        """
        if not ('/'+other_trajectory_name) in self._hdf5file:
            raise ValueError('Cannot merge `%s` and `%s`, because the second trajectory cannot '
                             'be found in my file.')

        for old_name, new_name in rename_dict.iteritems():
            # Iterate over all items that need to be merged
            split_name = old_name.split('.')
            old_location = '/'+other_trajectory_name+'/'+'/'.join(split_name)


            split_name = new_name.split('.')
            new_location = '/'+self._trajectory_name+'/'+'/'.join(split_name)

            # Get the data from the other trajectory
            try:
                old_group = self._hdf5file.get_node(old_location)
            except AttributeError:
                old_group = self._hdf5file.getNode(old_location)

            for node in old_group:
                # Now move or copy the data
                if move_nodes:
                    try:
                        self._hdf5file.move_node(where=old_location, newparent=new_location,
                                             name=node._v_name, createparents=True )
                    except AttributeError:
                        self._hdf5file.moveNode(where=old_location, newparent=new_location,
                                             name=node._v_name, createparents=True )
                else:
                    try:
                        self._hdf5file.copy_node(where=old_location, newparent=new_location,
                                              name=node._v_name, createparents=True,
                                              recursive=True)
                    except AttributeError:
                        self._hdf5file.copyNode(where=old_location, newparent=new_location,
                                              name=node._v_name, createparents=True,
                                              recursive=True)

            # And finally copy the attributes of leaf nodes
            # Attributes of group nodes are NOT copied, this has to be done
            # by the trajectory
            try:
                old_group._v_attrs._f_copy(where = self._hdf5file.get_node(new_location))
            except AttributeError:
                old_group._v_attrs._f_copy(where = self._hdf5file.getNode(new_location))

        self._trj_copy_table_entries(rename_dict, other_trajectory_name)

        if delete_trajectory:
            try:
                 self._hdf5file.remove_node(where='/', name=other_trajectory_name, recursive = True)
            except AttributeError:
                self._hdf5file.removeNode(where='/', name=other_trajectory_name, recursive = True)


    def _trj_prepare_merge(self, traj, changed_parameters):
        """Prepares a trajectory for merging.

        This function will already store extended parameters.

        :param traj: Target of merge
        :param changed_parameters: List of extended parameters (i.e. their names).

        """

        if not traj._stored:
            traj.f_store()

        # Update meta information
        infotable = getattr(self._overview_group,'info')
        insert_dict = self._all_extract_insert_dict(traj,infotable.colnames)
        self._all_add_or_modify_row(traj.v_name,insert_dict,infotable,index=0,
                                    flags=(HDF5StorageService.MODIFY_ROW,))


        # Store extended parameters
        for param_name in changed_parameters:
            param = traj.f_get(param_name)
            # First we delete the parameter
            try:
                self.store(pypetconstants.DELETE, param)
            except pt.NoSuchNodeError:
                pass # We can end up here if the parameter was never stored

            # And then we add it again
            self.store(pypetconstants.LEAF, param)

        # Increase the run table by the number of new runs
        run_table = getattr(self._overview_group,'runs')
        actual_rows = run_table.nrows
        self._all_fill_run_table_with_dummys(actual_rows, len(traj))

        add_table = self._overview_explored_parameters_runs


        # Extract parameter summary and if necessary create new explored parameter tables
        # in the result groups
        for run_name in traj.f_get_run_names():
            run_info = traj.f_get_run_information(run_name)
            run_info['name'] = run_name
            idx = run_info['idx']


            traj._set_explored_parameters_to_idx(idx)

            create_run_group = ('results.runs.%s' % run_name) in traj

            run_summary=self._srn_add_explored_params(run_name,traj._explored_parameters.values(),
                                                      add_table, create_run_group=create_run_group)


            run_info['parameter_summary'] = run_summary

            self._all_add_or_modify_row(run_name,run_info,run_table,index=idx,
                                        flags=(HDF5StorageService.MODIFY_ROW,))

        traj.f_restore_default()



    ######################## LOADING A TRAJECTORY #################################################

    def _trj_load_trajectory(self, msg, traj, as_new, load_parameters, load_derived_parameters,
                             load_results, load_other_data, force):
        """Loads a single trajectory from a given file.


        :param traj: The trajectory

        :param as_new: Whether to load trajectory as new

        :param load_parameters: How to load parameters and config

        :param load_derived_parameters: How to load derived parameters

        :param load_results: How to load results

        :param load_other_data: How to load anything not within the four subbranches

        :param force: Force load in case there is a pypet version mismatch

        You can specify how to load the parameters, derived parameters and results
        as follows:

        :const:`pypet.pypetconstants.LOAD_NOTHING`: (0)

            Nothing is loaded

        :const:`pypet.pypetconstants.LOAD_SKELETON`: (1)

            The skeleton including annotations are loaded, i.e. the items are empty.
            Non-empty items in RAM are left untouched.

        :const:`pypet.pypetconstants.LOAD_DATA`: (2)

            The whole data is loaded.
            Only empty or in RAM non-existing instance are filled with the
            data found on disk.

        :const:`pypet.pypetconstants.OVERWRITE_DATA`: (3)

            The whole data is loaded.
            If items that are to be loaded are already in RAM and not empty,
            they are emptied and new data is loaded from disk.


        If `as_new=True` the old trajectory is loaded into the new one, only parameters can be
        loaded. If `as_new=False` the current trajectory is completely replaced by the one
        on disk, i.e. the name from disk, the timestamp, etc. are assigned to `traj`.

        """
        # Some validity checks, if `as_new` is used correctly
        if (as_new and (load_derived_parameters != pypetconstants.LOAD_NOTHING or load_results !=
                        pypetconstants.LOAD_NOTHING or
                                load_other_data != pypetconstants.LOAD_NOTHING)):
            raise ValueError('You cannot load a trajectory as new and load the derived '
                                 'parameters and results. Only parameters are allowed.')


        if as_new and load_parameters != pypetconstants.LOAD_DATA:
            raise ValueError('You cannot load the trajectory as new and not load the data of '
                                 'the parameters.')

        loadconstants= (pypetconstants.LOAD_NOTHING, pypetconstants.LOAD_SKELETON,
                                   pypetconstants.LOAD_DATA, pypetconstants.OVERWRITE_DATA)

        if not (load_parameters in loadconstants and load_derived_parameters in loadconstants and
                load_results in loadconstants and load_other_data in loadconstants):
            raise ValueError('Please give a valid option on how to load data. Options for '
                             '`load_parameter`, `load_derived_parameters`, `load_results`, '
                             'and `load_other_data` are %s. See function documentation for '
                             'the semantics of the values.' % str(loadconstants))

        traj._stored = not as_new

        # Loads meta data like the name, timestamps etc.
        self._trj_load_meta_data(traj,as_new,force)

        self._logger.info('Loading trajectory `%s`.' % traj.v_name)

        # Load the annotations in case they have not been loaded before
        if traj.v_annotations.f_is_empty():
            self._ann_load_annotations(traj, self._trajectory_group)

        maximum_display_other = 10
        counter = 0

        children = self._trajectory_group._v_children
        for hdf5group_name in children:
            hdf5group = children[hdf5group_name]

            what = hdf5group._v_name

            load_subbranch = True
            if what == 'config':
                loading = load_parameters
            elif what == 'parameters':
                loading = load_parameters
            elif what == 'results':
                loading = load_results
            elif what == 'derived_parameters':
                loading = load_derived_parameters
            elif what == 'overview':
                continue
            else:
                loading = load_other_data
                load_subbranch = False

            if load_subbranch:
                # If the trajectory is loaded as new, we don't care about old config stuff
                # and only load the parameters
                if as_new and what == 'config':
                    loading=pypetconstants.LOAD_NOTHING

                # Load the subbranches recursively
                if loading != pypetconstants.LOAD_NOTHING:
                    self._logger.info('Loading branch `%s` in mode `%s`.' % (what, str(loading)))
                    self._tree_load_sub_branch(traj, traj, what, self._trajectory_group, loading,
                                               recursive=True,
                                               as_new=as_new)
            else:

                if loading != pypetconstants.LOAD_NOTHING:
                    counter += 1
                    if counter <= maximum_display_other:
                        self._logger.info('Loading branch/node `%s` in mode `%s`.' % (what, str(loading)))
                        if counter == maximum_display_other:
                            self._logger.info('To many branchs or nodes at root for display. '
                                              'I will not inform you about loading anymore. '
                                              'Branches are loaded silently in the background. '
                                              'Do not worry, I will not freeze! Pinky promise!!!')

                    self._tree_load_nodes(traj, traj, hdf5group, loading, recursive=True)


    def _trj_load_meta_data(self,traj, as_new, force):
        """Loads meta information about the trajectory

        Checks if the version number does not differ from current pypet version
        Loads, comment, timestamp, name, version from disk in case trajectory is not loaded
        as new. Updates the run information as well.

        """
        metatable = self._overview_group.info
        metarow = metatable[0]

        version = metarow['version']

        self._trj_check_version(version, force)

        if as_new:
            length = int(metarow['length'])
            for irun in range(length):
                traj._add_run_info(irun)
        else:
            traj._comment = str(metarow['comment'])
            traj._timestamp = float(metarow['timestamp'])
            traj._trajectory_timestamp = traj._timestamp
            traj._time = str(metarow['time'])
            traj._trajectory_time = traj._time
            traj._name = str(metarow['name'])
            traj._trajectory_name = traj._name
            traj._version = str(metarow['version'])

            single_run_table = self._overview_group.runs

            # Load the run information about the single runs
            for row in single_run_table.iterrows():
                name = str(row['name'])
                idx = int(row['idx'])
                timestamp = float(row['timestamp'])
                time = str(row['time'])
                completed = int(row['completed'])
                summary=str(row['parameter_summary'])
                hexsha = str(row['short_environment_hexsha'])


                # To allow backwards compatibility we need this try catch block
                try:
                    runtime = str(row['runtime'])
                    finish_timestamp = float(row['finish_timestamp'])
                except KeyError as ke:
                    runtime=''
                    finish_timestamp=0.0
                    self._logger.warning('Could not load runtime, ' + repr(ke))

                traj._single_run_ids[idx] = name
                traj._single_run_ids[name] = idx

                info_dict = {}
                info_dict['idx'] = idx
                info_dict['timestamp'] = timestamp
                info_dict['time'] = time
                info_dict['completed'] = completed
                info_dict['name'] = name
                info_dict['parameter_summary'] = summary
                info_dict['short_environment_hexsha'] = hexsha
                info_dict['runtime'] = runtime
                info_dict['finish_timestamp'] = finish_timestamp

                traj._run_information[name] = info_dict

            # Load the hdf5 config data:
            if 'hdf5_settings' in self._overview_group:
                hdf5_table = self._overview_group.hdf5_settings
                hdf5_row = hdf5_table[0]

                self.complib = str(hdf5_row['complib'])
                self.complevel = int(hdf5_row['complevel'])
                self.shuffle = bool(hdf5_row['shuffle'])
                self.fletcher32 = bool(hdf5_row['fletcher32'])
                self.pandas_format = str(hdf5_row['pandas_format'])
                self.pandas_append = bool(hdf5_row['pandas_append'])

                self._results_per_run = int(hdf5_row['results_per_run'])
                self._derived_parameters_per_run = int(hdf5_row['derived_parameters_per_run'])
                self._purge_duplicate_comments = bool(hdf5_row['purge_duplicate_comments'])
                self._overview_explored_parameters_runs = bool(hdf5_row['explored_parameters_runs'])

                for attr_name, table_name in self.NAME_TABLE_MAPPING.items():
                    attr_value = bool(hdf5_row[table_name])
                    setattr(self, attr_name, attr_value)


            else:
                self._logger.warning('Could not find `hdf5_settings` overview table. I will use the '
                                     'standard settings (for `complib`, `complevel` etc.) instead.')

    def _tree_load_sub_branch(self, traj, traj_node, branch_name, hdf5_group, load_data,
                              recursive=True, as_new=False):
        """Loads data starting from a node along a branch and starts recursively loading
        all data at end of branch.

        :param traj: The trajectory

        :param traj_node: The node from where loading starts

        :param branch_name:

            A branch along which loading progresses. Colon Notation is used:
            'group1.group2.group3' loads 'group1', then 'group2', then 'group3' and then finally
            recursively all children and children's children below 'group3'

        :param hdf5_group:

            HDF5 node in the file corresponding to `traj_node`.

        :param load_data:

            How to load the data

        :param recursive:

            If loading recursively

        :param as_new:

            If trajectory is loaded as new

        """
        split_names = branch_name.split('.')

        final_group_name = split_names.pop()

        for name in split_names:
            # First load along the branch
            hdf5_group = getattr(hdf5_group,name)

            self._tree_load_nodes(traj,traj_node, hdf5_group, load_data, recursive=False,
                                  as_new=as_new)

            traj_node = traj_node._children[name]


        # Then load recursively all data in the last group and below
        hdf5_group = getattr(hdf5_group,final_group_name)
        self._tree_load_nodes(traj,traj_node, hdf5_group, load_data, recursive=recursive)

    def _trj_check_version( self, version, force):
        """Checks for version mismatch

        Raises a VersionMismatchError if version of loaded trajectory and current pypet version
        do not match. In case of `force=True` error is not raised only a warning is emitted.

        """
        if version != VERSION and not force:
            raise pex.VersionMismatchError('Current pypet version is %s but your trajectory'
                                            ' was created with version %s.'
                                            ' Use >>force=True<< to perform your load regardless'
                                            ' of version mismatch.' %
                                           (VERSION, version))
        elif version != VERSION :
            self._logger.warning('Current pypet version is %s but your trajectory'
                                            ' was created with version %s.'
                                            ' Yet, you enforced the load, so I will'
                                            ' handle the trajectory despite the'
                                            ' version mismatch.' %
                                           (VERSION , version))


    #################################### Storing a Trajectory ####################################

    # def _trj_fill_run_table_with_dummys(self, traj, start=0):
    #     """Fills the `run` overview table with dummy information.
    #
    #     The table is later on filled by the single runs with the real information.
    #     `start` specifies how large the table is when calling this function.
    #
    #     The table might not be emtpy because a trajectory is enlarged due to expanding.
    #
    #     """
    #     runtable = getattr(self._overview_group,'runs')
    #
    #     for idx in range(start, len(traj)):
    #         name = traj.f_idx_to_run(idx)
    #         insert_dict = traj.f_get_run_information(name)
    #
    #         self._all_add_or_modify_row('Dummy Row', insert_dict, runtable,
    #                                     flags=(HDF5StorageService.ADD_ROW,))
    #
    #     runtable.flush()

    def _all_fill_run_table_with_dummys(self, start, stop):
        """Fills the `run` overview table with dummy information.

        The table is later on filled by the single runs with the real information.
        `start` specifies how large the table is when calling this function.

        The table might not be emtpy because a trajectory is enlarged due to expanding.

        """
        runtable = getattr(self._overview_group,'runs')

        for idx in range(start, stop):
            insert_dict={}
            insert_dict['idx'] = idx
            insert_dict['name'] = pypetconstants.FORMATTED_RUN_NAME % idx

            self._all_add_or_modify_row('Dummy Row', insert_dict, runtable,
                                        flags=(HDF5StorageService.ADD_ROW,))

        runtable.flush()

    def _trj_store_meta_data(self, traj):
        """ Stores general information about the trajectory in the hdf5file.

        The `info` table will contain the name of the trajectory, it's timestamp, a comment,
        the length (aka the number of single runs), and the current version number of pypet.

        Also prepares the desired overview tables and fills the `run` table with dummies.

        """

        # Description of the `info` table
        descriptiondict={'name': pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_LOCATION_LENGTH,
                                              pos=0),
                         'time': pt.StringCol(len(traj.v_time), pos=1),
                         'timestamp' : pt.FloatCol(pos=3),
                         'comment':  pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_COMMENT_LENGTH,
                                                  pos=4),
                         'length':pt.IntCol(pos=2),
                         'version' : pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_NAME_LENGTH,pos=5)}
                         # 'loaded_from' : pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_LOCATION_LENGTH)}

        infotable = self._all_get_or_create_table(where=self._overview_group, tablename='info',
                                               description=descriptiondict, expectedrows=len(traj))

        insert_dict = self._all_extract_insert_dict(traj, infotable.colnames)
        self._all_add_or_modify_row(traj.v_name, insert_dict, infotable,index=0,
                                    flags=(HDF5StorageService.ADD_ROW,
                                           HDF5StorageService.MODIFY_ROW))

        # Description of the `run` table
        rundescription_dict = {'name': pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_NAME_LENGTH,
                                                    pos=1),
                         'time': pt.StringCol(len(traj.v_time),pos=2),
                         'timestamp' : pt.FloatCol(pos=3),
                         'idx' : pt.IntCol(pos=0),
                         'completed' : pt.IntCol(pos=8),
                         'parameter_summary' : pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_COMMENT_LENGTH,
                                                            pos=6),
                         'short_environment_hexsha' : pt.StringCol(7,pos=7),
                         'finish_timestamp' : pt.FloatCol(pos=4),
                         'runtime' : pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_RUNTIME_LENGTH,
                                                  pos=5)}

        runtable = self._all_get_or_create_table(where=self._overview_group,
                                                 tablename='runs',
                                                 description=rundescription_dict)


        hdf5_description_dict = {'complib' : pt.StringCol(7, pos=0),
                                 'complevel' : pt.IntCol(pos=1),
                                 'shuffle' :  pt.BoolCol(pos=2),
                                 'fletcher32' : pt.BoolCol(pos=3),
                                  'pandas_append' : pt.BoolCol(pos=4),
                                  'pandas_format' : pt.StringCol(7, pos=5)}

        pos = 6
        for name, table_name in HDF5StorageService.NAME_TABLE_MAPPING.items():
            hdf5_description_dict[table_name] = pt.BoolCol(pos=pos)
            pos+=1

        # Store the hdf5 properties in an overview table
        hdf5_description_dict.update({'purge_duplicate_comments' : pt.BoolCol(pos=pos+2),
                                     'results_per_run' : pt.IntCol(pos=pos+3),
                                     'derived_parameters_per_run' : pt.IntCol(pos=pos+4),
                                     'explored_parameters_runs' : pt.BoolCol(pos=pos+1)})


        hdf5table = self._all_get_or_create_table(where=self._overview_group,
                                                  tablename='hdf5_settings',
                                                  description= hdf5_description_dict)

        insert_dict = {}
        for attr_name in self.ATTR_LIST:
            insert_dict[attr_name] = getattr(self, attr_name)

        for attr_name, table_name in self.NAME_TABLE_MAPPING.items():
            insert_dict[table_name] = getattr(self, attr_name)

        for attr_name, name in self.PR_ATTR_NAME_MAPPING.items():
            insert_dict[name] = getattr(self, attr_name)

        self._all_add_or_modify_row(traj.v_name, insert_dict, hdf5table, index=0,
                                    flags=(HDF5StorageService.ADD_ROW,HDF5StorageService.MODIFY_ROW))


        # Fill table with dummy entries starting from the current table size
        actual_rows = runtable.nrows
        self._all_fill_run_table_with_dummys(actual_rows, len(traj))

        # Store the annotations in the trajectory node
        self._ann_store_annotations(traj, self._trajectory_group)

        # Prepare the overview tables
        tostore_tables=[]

        for name, table_name in HDF5StorageService.NAME_TABLE_MAPPING.items():

            # Check if we want the corresponding overview table
            # If the trajectory does not contain information about the table
            # we assume it should be created.

            if getattr(self, name):
                tostore_tables.append(table_name)

        self._srvc_make_overview_tables(tostore_tables, traj)


    def _srvc_make_overview_tables(self, tables_to_make, traj=None):
        """Creates the overview tables in overview group"""
        for table_name in tables_to_make:
            # Prepare the tables desciptions, depending on which overview table we create
            # we need different columns
            paramdescriptiondict ={}
            expectedrows=0

            # Every overview table has a name and location column
            paramdescriptiondict['location']= pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_LOCATION_LENGTH,
                                                           pos=0)
            paramdescriptiondict['name']= pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_NAME_LENGTH,
                                                       pos=1)
            if not table_name == 'explored_parameters' and not 'groups' in table_name:
                paramdescriptiondict['value']=pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_VALUE_LENGTH)

            if table_name == 'config':
                if traj is not None:
                    expectedrows= len(traj._config)


            if table_name == 'parameters':
                if traj is not None:
                    expectedrows= len(traj._parameters)


            if table_name == 'explored_parameters':
                paramdescriptiondict['range']= pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_ARRAY_LENGTH)
                if traj is not None:
                    expectedrows=len(traj._explored_parameters)


            if table_name == 'results_trajectory':
                if traj is not None:
                    expectedrows=len(traj._results)

            if table_name == 'derived_parameters_trajectory':
                if traj is not None:
                    expectedrows=len(traj._derived_parameters)

            if table_name in ['derived_parameters_trajectory','results_trajectory',
                                  'derived_parameters_runs_summary', 'results_runs_summary',
                                  'config', 'parameters', 'explored_parameters']:

                if table_name.startswith('derived') or table_name.endswith('parameters'):
                    paramdescriptiondict['length']= pt.IntCol()

                paramdescriptiondict['comment']= pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_COMMENT_LENGTH)

            if table_name.endswith('summary'):
                paramdescriptiondict['number_of_items']= pt.IntCol(dflt=1)
                paramdescriptiondict['example_item_run_name'] = \
                    pt.StringCol(len(pypetconstants.RUN_NAME)+pypetconstants.FORMAT_ZEROS+3,pos=2)

            # Check if the user provided an estimate of the amount of results per run
            # This can help to speed up storing
            if table_name.startswith('derived_parameters_runs'):

                expectedrows = self._derived_parameters_per_run

                if not table_name.endswith('summary') and traj is not None:
                    expectedrows *= len(traj)


            if table_name.startswith('results_runs'):
                expectedrows = self._results_per_run

                if not expectedrows <=0:
                    if not table_name.endswith('summary') and traj is not None:
                        expectedrows *= len(traj)

            if expectedrows>0:
                paramtable = self._all_get_or_create_table(where=self._overview_group,
                                                           tablename=table_name,
                                                           description=paramdescriptiondict,
                                                           expectedrows=expectedrows)
            else:
                paramtable = self._all_get_or_create_table(where=self._overview_group,
                                                           tablename=table_name,
                                                           description=paramdescriptiondict)

            # # Index the summary tables for faster look up
            # # They are searched by the individual runs later on
            # if table_name.endswith('summary'):
            #     try:
            #         paramtable.autoindex=True
            #     except AttributeError:
            #         paramtable.autoIndex=True
            #     if not paramtable.indexed:
            #         try:
            #             paramtable.cols.location.create_index(optlevel=8, kind='full')
            #             paramtable.cols.name.create_index(optlevel=8, kind='full')
            #         except AttributeError:
            #             paramtable.cols.location.createIndex(optlevel=8, kind='full')
            #             paramtable.cols.name.createIndex(optlevel=8, kind='full')


            paramtable.flush()

    def _trj_store_trajectory(self, traj, only_init = False):
        """ Stores a trajectory to an hdf5 file

        Stores all groups, parameters and results

        """
        if not only_init:
            self._logger.info('Start storing Trajectory `%s`.' % self._trajectory_name)
        else:
            self._logger.info('Initialising storage or updating meta data of Trajectory `%s`.' %
                         self._trajectory_name)

        # In case we accidentally chose a trajectory name that already exist
        # We do not want to mess up the stored trajectory but raise an Error
        if not traj._stored and self._trajectory_group._v_nchildren > 0:
            raise RuntimeError('You want to store a completely new trajectory with name'
                               ' `%s` but this trajectory is already found in file `%s`' %
                               (traj.v_name,self._filename))

        # Extract HDF5 settings from the trajectory
        self._srvc_check_hdf_properties(traj)

        # Store meta information
        self._trj_store_meta_data(traj)

        # # Store recursively the config subtree
        # self._tree_store_recursively(pypetconstants.LEAF,traj.config,self._trajectory_group)

        if not only_init:

            counter = 0
            maximum_display_other = 10
            name_set = set(['parameters', 'config', 'derived_parameters', 'results'])

            for child_name in traj._children:

                if child_name in name_set:
                    self._logger.info('Storing branch `%s`.' % child_name)
                else:
                    counter += 1
                    if counter <= maximum_display_other:
                        self._logger.info('Storing branch/node `%s`.' % child_name)
                        if counter == maximum_display_other:
                            self._logger.info('To many branches or nodes at root for display. '
                                              'I will not inform you about storing anymore. '
                                              'Branches are stored silently in the background. '
                                              'Do not worry, I will not freeze! Pinky promise!!!')

                # Store recursively the derived parameters subtree
                self._tree_store_nodes(pypetconstants.LEAF, traj._children[child_name],
                                                 self._trajectory_group)


            self._logger.info('Finished storing Trajectory `%s`.' % self._trajectory_name)
        else:
            self._logger.info('Finished init or meta data update for `%s`.' %
                              self._trajectory_name)

        traj._stored=True

    def _tree_store_sub_branch(self, msg, traj_node, branch_name, hdf5_group, recursive=True):
        """Stores data starting from a node along a branch and starts recursively loading
        all data at end of branch.

        :param msg: 'LEAF'

        :param traj_node: The node where storing starts

        :param branch_name:

            A branch along which storing progresses. Colon Notation is used:
            'group1.group2.group3' loads 'group1', then 'group2', then 'group3', and then finally
            recursively all children and children's children below 'group3'.

        :param hdf5_group:

            HDF5 node in the file corresponding to `traj_node`

        """

        split_names = branch_name.split('.')

        leaf_name = split_names.pop()

        for name in split_names:
            # Store along a branch
            traj_node = traj_node._children[name]

            self._tree_store_nodes(msg,traj_node,hdf5_group, recursive=False)

            hdf5_group=getattr(hdf5_group, name)

        # Store final group and recursively everything below it
        traj_node = traj_node._children[leaf_name]

        self._tree_store_nodes(msg,traj_node,hdf5_group, recursive)


    ########################  Storing and Loading Sub Trees #######################################

    def _tree_store_tree(self, traj_node, child_name, recursive):
        """Stores a node and potentially recursively all nodes below

        :param traj_node: Parent node where storing starts

        :param child_name: Name of child node

        :param recursive: Whether to store everything below `traj_node`.

        """
        location = traj_node.v_full_name

        # Get parent hdf5 node
        hdf5_location = location.replace('.','/')
        try:
            if location=='':
                parent_hdf5_node = self._trajectory_group
            else:
                try:
                    parent_hdf5_node = self._hdf5file.get_node(where=self._trajectory_group,
                                                              name=hdf5_location)
                except AttributeError:
                    parent_hdf5_node = self._hdf5file.getNode(where=self._trajectory_group,
                                                              name=hdf5_location)

            # Store node and potentially everything below it
            self._tree_store_sub_branch(pypetconstants.LEAF, traj_node, child_name, parent_hdf5_node,
                                        recursive=recursive)

        except pt.NoSuchNodeError:
            self._logger.warning('Cannot store `%s` the parental hdf5 node with path `%s` does '
                               'not exist on disk.' %
                               (traj_node.v_name,hdf5_location))


            if traj_node.v_is_leaf:
                self._logger.error('Cannot store `%s` the parental hdf5 node with path `%s` does '
                               'not exist on disk! The child you want to store is a leaf node,'
                               'that cannot be stored without the parental node existing on '
                               'disk.' %
                               (traj_node.v_name,hdf5_location))
                raise
            else:
                self._logger.warning('I will try to store the path from trajectory root to '
                                     'the child now.')
                self._tree_store_sub_branch(pypetconstants.LEAF, traj_node._nn_interface._root_instance,
                                           traj_node.v_full_name+'.'+child_name,
                                           self._trajectory_group,
                                           recursive=recursive)



    def _tree_load_tree(self, parent_traj_node, child_name, recursive, load_data, trajectory):
        """Loads a specific tree node and potentially all nodes below

        :param parent_traj_node: parent node of node to load in trajectory

        :param child_name: Name (!) of node to be loaded

        :param recursive: Whether to load everything below the child

        :param load_data: How to load the data

        :param trajectory: The trajectory object

        """
        hdf5_node_name =parent_traj_node.v_full_name.replace('.','/')

        # Get child node to load
        if hdf5_node_name == '':
                hdf5_node = self._trajectory_group
        else:
            try:
                try:
                    hdf5_node = self._hdf5file.get_node(where=self._trajectory_group,name = hdf5_node_name)
                except AttributeError:
                    hdf5_node = self._hdf5file.getNode(where=self._trajectory_group,name = hdf5_node_name)
            except pt.NoSuchNodeError:
                self._logger.error('Cannot load `%s` the hdf5 node `%s` does not exist!'
                                    % (child_name, hdf5_node_name))
                raise

        self._tree_load_sub_branch(trajectory, parent_traj_node, child_name, hdf5_node, load_data=load_data,
                                   recursive = recursive)


    def _tree_load_nodes(self, traj, parent_traj_node, hdf5group,
                              load_data=pypetconstants.UPDATE_SKELETON, recursive=True,
                              as_new=False):
        """Loads a node from hdf5 file and if desired recursively everything below

        :param traj: The trajectory object
        :param parent_traj_node: The parent node whose child should be loaded
        :param hdf5group: The hdf5 group containing the child to be loaded
        :param load_data: How to load the data
        :param recursive: Whether loading recursively below hdf5group
        :param as_new: If trajectory is loaded as new

        """
        if load_data == pypetconstants.LOAD_NOTHING:
            return

        path_name = parent_traj_node.v_full_name
        name = hdf5group._v_name
        is_leaf = self._all_get_from_attrs(hdf5group,HDF5StorageService.LEAF)

        if is_leaf:
            # In case we have a leaf node, we need to check if we have to create a new
            # parameter or result
            full_name = '%s.%s' % (path_name,name)

            in_trajectory =  name in parent_traj_node._children

            if in_trajectory:
                instance=parent_traj_node._children[name]

                # If we want to update data and the item already contains some we're good
                if load_data == pypetconstants.OVERWRITE_DATA:
                    if instance.v_is_parameter:
                        instance.f_unlock()
                    instance.f_empty()
                    instance.v_annotations.f_empty()

                # Load annotations if they are empty
                if instance.v_annotations.f_is_empty():
                    self._ann_load_annotations(instance, hdf5group)

                # If we want to update the skeleton and the item exists we're good
                if load_data == pypetconstants.UPDATE_SKELETON:
                    return

                # If the instance is non-empty we do not need to load it
                if not instance.f_is_empty():
                    return

            # Otherwise we need to create a new instance
            if not in_trajectory:

                class_name = self._all_get_from_attrs(hdf5group,HDF5StorageService.CLASS_NAME)

                comment = self._all_get_from_attrs(hdf5group,HDF5StorageService.COMMENT)
                if comment is None:
                    comment = ''

                range_length = self._all_get_from_attrs(hdf5group, HDF5StorageService.LENGTH)

                if not range_length is None and range_length != len(traj):
                        raise RuntimeError('Something is completely odd. You load parameter'
                                               ' `%s` of length %d into a trajectory of length'
                                               ' %d. They should be equally long!'  %
                                               (full_name,range_length,len(traj)))

                # Create the instance with the appropriate constructor
                class_constructor = traj._create_class(class_name)

                instance = class_constructor(name,
                                             comment=comment)

                instance._stored = not as_new
                if instance.v_is_parameter:
                    instance._explored = range_length is not None

                # Add the instance to the trajectory tree
                parent_traj_node._nn_interface._add_generic(parent_traj_node,
                                                            type_name = nn.LEAF,
                                                            group_type_name = nn.GROUP,
                                                            args=(instance,), kwargs={},
                                                            add_prefix=False)

                # If it has a range we add it to the explored parameters
                if range_length:
                    traj._explored_parameters[instance.v_full_name]=instance

                self._ann_load_annotations(instance, node=hdf5group)

            if load_data in (pypetconstants.LOAD_DATA, pypetconstants.OVERWRITE_DATA):
                # Load data into the instance
                self._prm_load_parameter_or_result(instance, _hdf5_group=hdf5group)

            self._node_processing_timer.signal_update()

        else:
            # Else we are dealing with a group node
            if not name in parent_traj_node._children:
                # If the group does not exist create it

                comment = self._all_get_from_attrs(hdf5group,HDF5StorageService.COMMENT)
                if comment is None:
                    comment = ''

                new_traj_node = parent_traj_node._nn_interface._add_generic(parent_traj_node,
                                               type_name = nn.GROUP,
                                               group_type_name = nn.GROUP,
                                               args = (name,
                                                       comment),
                                               kwargs={},
                                               add_prefix=False)

                new_traj_node._stored = not as_new

            else:
                new_traj_node = parent_traj_node._children[name]

                if load_data == pypetconstants.OVERWRITE_DATA:
                    new_traj_node.v_annotations.f_empty()

            # Load annotations if they are empty
            if new_traj_node.v_annotations.f_is_empty():
                self._ann_load_annotations(new_traj_node, hdf5group)

            self._node_processing_timer.signal_update()

            if recursive:
                # We load recursively everything below it
                children = hdf5group._v_children
                for new_hdf5group_name in children:
                    new_hdf5group = children[new_hdf5group_name]
                    if not isinstance(new_hdf5group, pt.Group):
                        continue
                    self._tree_load_nodes(traj,new_traj_node, new_hdf5group,load_data)


    def _tree_store_nodes(self,msg, traj_node, parent_hdf5_group, recursive = True):
        """Stores a node to hdf5 and if desired stores recursively everything below it.

        :param msg: 'LEAF'
        :param traj_node: Node to be stored
        :param parent_hdf5_group: Parent hdf5 groug
        :param recursive: Whether to store recursively the subtree

        """

        name = traj_node.v_name

        store_new = False
        store_msg=msg

        # If the node does not exist in the hdf5 file create it
        if not hasattr(parent_hdf5_group,name):
            store_new = True
            try:
                new_hdf5_group = self._hdf5file.create_group(where=parent_hdf5_group,name=name)
            except AttributeError:
                new_hdf5_group = self._hdf5file.createGroup(where=parent_hdf5_group,name=name)
        else:
            new_hdf5_group = getattr(parent_hdf5_group,name)

        if traj_node.v_is_leaf:
            if store_new:
                # If we have a leaf node, store it as a parameter or result
                self._prm_store_parameter_or_result(store_msg, traj_node,
                                                    _hdf5_group=new_hdf5_group,
                                                    _newly_created=True)
            else:
                self._logger.debug('Already found `%s` on disk I will not store it!' %
                               traj_node.v_full_name)

            self._node_processing_timer.signal_update()

        else:
            # Else store it as a group node

            # We have to do the following check to be sure that the group node was not
            # build on the fly via `f_store_item`.
            store_new = (store_new  or
                         (not traj_node.v_annotations.f_is_empty()
                         and not HDF5StorageService.ANNOTATED in new_hdf5_group._v_attrs) or
                         (traj_node.v_comment != '' and
                         not HDF5StorageService.COMMENT not in new_hdf5_group._v_attrs) )

            if store_new:
                self._grp_store_group(traj_node,_hdf5_group=new_hdf5_group)
            else:
                self._logger.debug('Already found `%s` on disk I will not store it!' %
                               traj_node.v_full_name)

            self._node_processing_timer.signal_update()

            if recursive:
                # And if desired store recursively the subtree
                for child in traj_node._children.itervalues():
                    self._tree_store_nodes(store_msg,child,new_hdf5_group)


    ######################## Storing a Single Run ##########################################
    def _srn_store_single_run(self, single_run, store_data, store_final):
        """ Stores a single run instance to disk (only meta data)"""

        if store_data:
            self._logger.info('Storing Data of single run `%s`.' % single_run.v_name)
            for group_name in single_run._run_parent_groups:
                group = single_run._run_parent_groups[group_name]
                if group.f_contains(single_run.v_name):
                    self._tree_store_tree(group, single_run.v_name, recursive=True)

        if store_final:
            self._logger.info('Finishing Storage of single run `%s`.' % single_run.v_name)
            idx = single_run.v_idx

            add_table = self._overview_explored_parameters_runs

            # For better readability and if desired add the explored parameters to the results
            # Also collect some summary information about the explored parameters
            # So we can add this to the `run` table
            run_summary = self._srn_add_explored_params(single_run.v_name,
                                                        single_run._explored_parameters.values(),
                                                        add_table)

            # Finally, add the real run information to the `run` table
            runtable = getattr(self._overview_group,'runs')

            # If the table is not large enough already (maybe because the trajectory got expanded
            # We have to manually increase it here
            actual_rows = runtable.nrows
            if idx+1 > actual_rows:
                self._all_fill_run_table_with_dummys(actual_rows, idx+1)

            insert_dict = self._all_extract_insert_dict(single_run, runtable.colnames)
            insert_dict['parameter_summary'] = run_summary
            insert_dict['completed'] = 1

            self._hdf5file.flush()
            self._all_add_or_modify_row(single_run, insert_dict, runtable,
                                        index=idx, flags=(HDF5StorageService.MODIFY_ROW,))

    def _srn_add_explored_params(self, run_name, paramlist, add_table, create_run_group=False):
        """If desired adds an explored parameter overview table to the results in each
        single run and summarizes the parameter settings.

        :param run_name: Name of the single run

        :param paramlist: List of explored parameters

        :param add_table: Whether to add the overview table

        :param create_run_group:

            If a group with the particular name should be created if it does not exist.
            Might be necessary when trajectories are merged.

        """

        # Layout of overview table
        paramdescriptiondict={'name': pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_NAME_LENGTH),
                                'value' :pt.StringCol(pypetconstants.HDF5_STRCOL_MAX_VALUE_LENGTH)}

        location= 'results.runs.'+run_name

        where = location
        where = where.replace('.','/')

        if not where in self._trajectory_group:
            if create_run_group:
                self._all_create_or_get_groups(location)
            else:
                add_table = False

        if add_table:

            rungroup = getattr(self._trajectory_group, where)

            # Check if the table already exists
            if 'explored_parameters' in rungroup:
                # This can happen if trajectories are merged
                # If the number of explored parameters changed due to merging we
                # need to create the table new in order to show the correct parameters
                paramtable = getattr(rungroup,'explored_parameters')

                # If more parameters became explored we need to create the table new
                if paramtable.nrows != len(paramlist):
                    del paramtable
                    try:
                        self._hdf5file.remove_node(where=rungroup, name='explored_parameters')
                    except AttributeError:
                        self._hdf5file.removeNode(where=rungroup, name='explored_parameters')
                else:
                    add_table=False

            if not 'explored_parameters' in rungroup:
                try:
                    paramtable = self._hdf5file.create_table(where=rungroup,
                                                            name='explored_parameters',
                                                            description=paramdescriptiondict,
                                                            title='explored_parameters',
                                                            filters=self._get_filters())
                except AttributeError:
                    paramtable = self._hdf5file.createTable(where=rungroup,
                                                            name='explored_parameters',
                                                            description=paramdescriptiondict,
                                                            title='explored_parameters',
                                                            filters=self._get_filters())

        runsummary = ''
        paramlist = sorted(paramlist, key= lambda name: name.v_name + name.v_location)
        for idx,expparam in enumerate(paramlist):

            # Create the run summary for the `run` overview
            if idx > 0:
                runsummary += ',   '

            valstr = expparam.f_val_to_str()

            if len(valstr) >= pypetconstants.HDF5_STRCOL_MAX_COMMENT_LENGTH:
                valstr = valstr[0:pypetconstants.HDF5_STRCOL_MAX_COMMENT_LENGTH-3]
                valstr+='...'

            if expparam.v_name in runsummary:
                param_name = expparam.v_full_name
            else:
                param_name = expparam.v_name

            runsummary = runsummary + param_name + ': ' +valstr

            # If Add the explored parameter overview table if dersired and necessary
            if add_table:
                self._all_store_param_or_result_table_entry(expparam, paramtable,
                                                        (HDF5StorageService.ADD_ROW,))

        return runsummary



    ################# Methods used across Storing and Loading different Items #####################

    def _all_find_param_or_result_entry_and_return_iterator(self, param_or_result, table):
        """Searches for a particular entry in `table` based on the name and location
        of `param_or_result` and returns an iterator over the found rows
        (should contain only a single row).

        """
        location = param_or_result.v_location
        name = param_or_result.v_name

        condvars = {'namecol' : table.cols.name, 'locationcol' : table.cols.location,
                        'name' : name, 'location': location}

        condition = """(namecol == name) & (locationcol == location)"""

        return table.where(condition,condvars=condvars)



    @staticmethod
    def _all_get_table_name(where, creator_name):
        """Returns an overview table name for a given subtree name

        :param where:

            Either `parameters`, `config`, `derived_parameters`, or `results`

        :param creator_name:

            Either `trajectory` or `run_XXXXXXXXX`

        :return: Name of overview table

        """
        if where in ['config','parameters']:
                return where
        else:
            if creator_name == 'trajectory':
                return '%s_trajectory' % where
            else:
                return '%s_runs' % where


    def _all_store_param_or_result_table_entry(self,instance,table, flags,
                                               additional_info=None):
        """Stores a single row into an overview table

        :param instance: A parameter or result instance

        :param table: Table where row will be inserted

        :param flags:

            Flags how to insert into the table. Potential Flags are
            `ADD_ROW`, `REMOVE_ROW`, `MODIFY_ROW`

        :param additional_info:

            Dictionary containing information that cannot be extracted from
            `instance`, but needs to be inserted, too.


        """
        #assert isinstance(table, pt.Table)

        location = instance.v_location
        name = instance.v_name
        fullname = instance.v_full_name


        if flags==(HDF5StorageService.ADD_ROW,):
            # If we are sure we only want to add a row we do not need to search!
            condvars = None
            condition = None
        else:
            # Condition to search for an entry
            condvars = {'namecol' : table.cols.name, 'locationcol' : table.cols.location,
                        'name' : name, 'location': location}

            condition = """(namecol == name) & (locationcol == location)"""


        colnames = set(table.colnames)

        if HDF5StorageService.REMOVE_ROW in flags:
            # If we want to remove a row, we don't need to extract information
            insert_dict={}
        else:
            # Extract information to insert from the instance and the additional info dict
            insert_dict = self._all_extract_insert_dict(instance, colnames, additional_info)

        # Write the table entry
        self._all_add_or_modify_row(fullname, insert_dict, table, condition=condition,
                                    condvars=condvars,flags=flags)


    def _all_get_or_create_table(self,where,tablename,description,expectedrows=None):
        """Creates a new table, or if the table already exists, returns it."""
        where_node = self._hdf5file.getNode(where)

        if not tablename in where_node:
            if not expectedrows is None:
                try:
                    table = self._hdf5file.create_table(where=where_node, name=tablename,
                                                   description=description, title=tablename,
                                                   expectedrows=expectedrows,
                                                   filters=self._get_filters())
                except AttributeError:
                    table = self._hdf5file.createTable(where=where_node, name=tablename,
                                                   description=description, title=tablename,
                                                   expectedrows=expectedrows,
                                                   filters=self._get_filters())
            else:
                try:
                    table = self._hdf5file.create_table(where=where_node, name=tablename,
                                                   description=description, title=tablename,
                                                   filters=self._get_filters())
                except AttributeError:
                    table = self._hdf5file.createTable(where=where_node, name=tablename,
                                                   description=description, title=tablename,
                                                   filters=self._get_filters())
        else:
            try:
                table = where_node._f_get_child(tablename)
            except AttributeError:
                table = where_node._f_getChild(tablename)

        return table

    def _all_get_node_by_name(self,name):
        """Returns an HDF5 node by the path specified in `name`"""
        path_name = name.replace('.','/')
        where = '/%s/%s' %(self._trajectory_name,path_name)

        try:
            return self._hdf5file.get_node(where=where)
        except AttributeError:
            return self._hdf5file.getNode(where=where)

    @staticmethod
    def _all_attr_equals(ptitem, name,value):
        """Checks if a given hdf5 node attribute exists and if so if it matches the `value`."""
        try:
            return ptitem._v_attrs[name] == value
        except KeyError:
            return False

    @staticmethod
    def _all_get_from_attrs(ptitem, name):
        """Gets an attribute `name` from `ptitem`, returns None if attribute does not exist."""
        # if name in ptitem._v_attrs:
        #     return ptitem._v_attrs[name]
        # else:
        #     return None
        try:
            return ptitem._v_attrs[name]
        except KeyError:
            return None

    def _all_set_attributes_to_recall_natives(self, data, ptitem, prefix):
        """Stores original data type to hdf5 node attributes for preserving the data type.

        :param data:

            Data to be stored

        :param ptitem:

            HDF5 node to store data types as attributes. Can also be just a PTItemMock.

        :param prefix:

            String prefix to label and name data in HDF5 attributes

        """

        def _set_attribute_to_item_or_dict(item, name,val):
            """Stores `val` with `name` into `item_or_dict`.

            `item` is either and HDF5 node or a python dictionary as PTItemMock.

            """
            try:
                item._f_setattr(name,val)
            except AttributeError:
                item._f_setAttr(name,val)


        # If `data` is a container, remember the container type
        if type(data) is tuple:
            _set_attribute_to_item_or_dict(ptitem,prefix+HDF5StorageService.COLL_TYPE,
                            HDF5StorageService.COLL_TUPLE)

        elif type(data) is list:
            _set_attribute_to_item_or_dict(ptitem,prefix+HDF5StorageService.COLL_TYPE,
                            HDF5StorageService.COLL_LIST)

        elif type(data) is np.ndarray:
            _set_attribute_to_item_or_dict(ptitem,prefix+HDF5StorageService.COLL_TYPE,
                            HDF5StorageService.COLL_NDARRAY)

        elif type(data) is np.matrix:
            _set_attribute_to_item_or_dict(ptitem,prefix+HDF5StorageService.COLL_TYPE,
                                           HDF5StorageService.COLL_MATRIX)

        elif type(data) in pypetconstants.PARAMETER_SUPPORTED_DATA:
            _set_attribute_to_item_or_dict(ptitem,prefix+HDF5StorageService.COLL_TYPE,
                            HDF5StorageService.COLL_SCALAR)

            strtype = repr(type(data))

            if not strtype in pypetconstants.PARAMETERTYPEDICT:
                raise TypeError('I do not know how to handle `%s` its type is `%s`.' %
                               (str(data),repr(type(data))))

            _set_attribute_to_item_or_dict(ptitem,prefix+HDF5StorageService.SCALAR_TYPE,strtype)

        elif type(data) is dict:
            _set_attribute_to_item_or_dict(ptitem,prefix+HDF5StorageService.COLL_TYPE,
                            HDF5StorageService.COLL_DICT)

        else:
            raise TypeError('I do not know how to handle `%s` its type is `%s`.' %
                               (str(data),repr(type(data))))

        if type(data) in (list,tuple):
            # If data is a list or tuple we need to remember the data type of the elements
            # in the list or tuple.
            # We do NOT need to remember the elements of `dict` explicitly, though.
            # `dict` is stored
            # as an `ObjectTable` and thus types are already conserved.
            if len(data) > 0:
                strtype = repr(type(data[0]))

                if not strtype in pypetconstants.PARAMETERTYPEDICT:
                    raise TypeError('I do not know how to handle `%s` its type is '
                                       '`%s`.' % (str(data),strtype))

                _set_attribute_to_item_or_dict(ptitem,prefix +
                                                    HDF5StorageService.SCALAR_TYPE,strtype)


    def _all_recall_native_type(self, data, ptitem, prefix):
        """Checks if loaded data has the type it was stored in. If not converts it.

        :param data: Data item to be checked and converted
        :param ptitem: HDf5 Node or Leaf from where data was loaded
        :param prefix: Prefix for recalling the data type from the hdf5 node attributes

        :return:

            Tuple, first item is the (converted) `data` item, second boolean whether
            item was converted or not.

        """
        typestr = self._all_get_from_attrs(ptitem,prefix+HDF5StorageService.SCALAR_TYPE)
        type_changed = False

        # Check what the original data type was from the hdf5 node attributes
        if self._all_attr_equals(ptitem, prefix+HDF5StorageService.COLL_TYPE,
                                 HDF5StorageService.COLL_SCALAR):
            # Here data item was a scalar

            if isinstance(data, np.ndarray):
                # If we recall a numpy scalar, pytables loads a 1d array :-/
                # So we have to change it to a real scalar value
                data = np.array([data])[0]
                type_changed = True


            if not typestr is None:
                # Check if current type and stored type match
                # if not convert the data
                if not typestr == repr(type(data)):
                    data = pypetconstants.PARAMETERTYPEDICT[typestr](data)
                    type_changed = True


        elif (self._all_attr_equals(ptitem, prefix+HDF5StorageService.COLL_TYPE,
                                     HDF5StorageService.COLL_TUPLE) or
                self._all_attr_equals(ptitem, prefix+HDF5StorageService.COLL_TYPE,
                                       HDF5StorageService.COLL_LIST)):
            # Here data item was originally a tuple or a list

            if not isinstance(data,(list,tuple)):
                # If the original type cannot be recalled, first convert it to a list
                type_changed=True
                data = list(data)

            if len(data)>0:
                first_item = data[0]
            else:
                first_item = None

            if not first_item is None:
                # Check if the type of the first item was conserved
                if not typestr == repr(type(first_item)):

                    if not isinstance(data, list):
                        data = list(data)

                    # If type was not conserved we need to convert all items
                    # in the list or tuple
                    for idx,item in enumerate(data):
                        data[idx] = pypetconstants.PARAMETERTYPEDICT[typestr](item)
                        type_changed = True

            if self._all_attr_equals(ptitem, prefix+HDF5StorageService.COLL_TYPE,
                                      HDF5StorageService.COLL_TUPLE):
                # If it was originally a tuple we need to convert it back to tuple
                if not isinstance(data, tuple):
                    data = tuple(data)
                    type_changed = True

        elif self._all_attr_equals(ptitem, prefix+HDF5StorageService.COLL_TYPE,
                                      HDF5StorageService.COLL_MATRIX):
                # Here data item was originally a matrix
                data = np.matrix(data)
                type_changed = True

        return data, type_changed

    def _all_add_or_modify_row(self, item_name, insert_dict, table,index=None, condition=None,
                               condvars=None,
                               flags=(ADD_ROW, MODIFY_ROW,)):
        """Adds or changes a row in a pytable.

        :param item_name: Name of item, the row is about, only important for throwing errors.

        :param insert_dict:

            Dictionary of data that is about to be inserted into the pytables row.

        :param table:

            The table to insert or modify a row in

        :param index:

            Index of row to be modified. Instead of an index a search condition can be
            used as well, see below.

        :param condition:

            Condition to search for in the table

        :param condvars:

            Variables for the search condition

        :param flags:

            Flags whether to add, modify, or remove a row in the table


        """

        # You can only specify either an index or a condition not both
        if not index is None and not condition is None:
            raise ValueError('Please give either a condition or an index or none!')
        elif not condition is None:
            row_iterator = table.where(condition,condvars=condvars)
        elif not index is None:
            row_iterator = table.iterrows(index,index+1)
        else:
            row_iterator = None

        try:
            row = row_iterator.next()
        except AttributeError:
            row = None
        except StopIteration:
            row = None


        if ((HDF5StorageService.MODIFY_ROW in flags or HDF5StorageService.ADD_ROW in flags) and
                HDF5StorageService.REMOVE_ROW in flags):
            # You cannot remove and modify or add at the same time
            raise ValueError('You cannot add or modify and remove a row at the same time.')

        if row is None and HDF5StorageService.ADD_ROW in flags:
            # Here we add a new row

            row = table.row


            self._all_insert_into_row(row, insert_dict)

            row.append()

        elif row is not None and HDF5StorageService.MODIFY_ROW in flags:
            # Here we modify an existing row

            self._all_insert_into_row(row,insert_dict)

            row.update()

        elif HDF5StorageService.REMOVE_ROW in flags:
            # Here we delete an existing row

            if row is not None:
                # Only delete if the row does exist otherwise we do not have to do anything
                rownumber = row.nrow
                multiple_entries = False

                try:
                    row_iterator.next()
                    multiple_entries = True
                except StopIteration:
                    pass

                if  multiple_entries:
                     raise RuntimeError('There is something entirely wrong, `%s` '
                                        'appears more than once in table %s.'
                                        %(item_name,table._v_name))

                try:
                    try:
                        table.remove_rows(rownumber)
                    except AttributeError:
                        table.removeRows(rownumber)
                except NotImplementedError:
                    pass # We get here if we try to remove the last row of a table
                    # there is nothing we can do except for keeping it :(
        else:
            raise ValueError('Something is wrong, you might not have found '
                               'a row, or your flags are not set approprialty')

        ## Check if there are 2 entries which should not happen
        multiple_entries = False
        try:
            row_iterator.next()
            multiple_entries = True
        except StopIteration:
            pass
        except AttributeError:
            pass

        if  multiple_entries:
             raise RuntimeError('There is something entirely wrong, `%s` '
                                'appears more than once in table %s.'
                                % (item_name,table._v_name))

        # Check if we added something. Note that row is also not None in case REMOVE_ROW,
        # then it refers to the deleted row
        if HDF5StorageService.REMOVE_ROW not in flags and row is None:
            raise RuntimeError('Could not add or modify entries of `%s` in '
                               'table %s' %(item_name,table._v_name))
        table.flush()




    def _all_insert_into_row(self, row, insert_dict):
        """Copies data from `insert_dict` into a pytables `row`."""
        for key, val in insert_dict.items():
            try:
                row[key] = val
            except KeyError as ke:
                self._logger.warning('Could not write `%s` into a table, ' % key+ repr(ke))


    def _all_extract_insert_dict(self,item, colnames, additional_info=None):
        """Extracts information from a given item to be stored into a pytable row.

        Items can be a variety of things here, trajectories, single runs, group node,
        parameters, results.

        :param item: Item from which data should be extracted

        :param colnames: Names of the columns in the pytable

        :param additional_info: (dict)

            Additional information that should be stored into the pytable row that cannot be
            read out from `item`.

        :return: Dictionary containing the data to be inserted into a row

        """
        insert_dict={}

        if 'length' in colnames:
            insert_dict['length'] = len(item)

        if 'comment' in colnames:
            comment = self._all_cut_string(item.v_comment,
                                           pypetconstants.HDF5_STRCOL_MAX_COMMENT_LENGTH,
                                           self._logger)

            insert_dict['comment'] = comment

        if 'location' in colnames:
            insert_dict['location'] = item.v_location

        if 'name' in colnames:
            insert_dict['name'] = item.v_name

        if 'class_name' in colnames:
            insert_dict['class_name'] = item.f_get_class_name()

        if 'value' in colnames:
            insert_dict['value'] = self._all_cut_string(item.f_val_to_str(),
                                    pypetconstants.HDF5_STRCOL_MAX_VALUE_LENGTH, self._logger)

        if 'example_item_run_name' in colnames:
            insert_dict['example_item_run_name'] = additional_info['example_item_run_name']

        if 'idx' in colnames:
            insert_dict['idx'] = item.v_idx

        if 'time' in colnames:
            insert_dict['time'] = item.v_time

        if 'timestamp' in colnames:
            insert_dict['timestamp'] = item.v_timestamp

        if 'range' in colnames:
            insert_dict['range'] = self._all_cut_string(str(item.f_get_range()),
                                    pypetconstants.HDF5_STRCOL_MAX_ARRAY_LENGTH, self._logger)

        # To allow backwards compatibility
        if 'array' in colnames:
            insert_dict['array'] = self._all_cut_string(str(item.f_get_range()),
                                    pypetconstants.HDF5_STRCOL_MAX_ARRAY_LENGTH, self._logger)

        if 'version' in colnames:
            insert_dict['version'] = item.v_version

        if 'finish_timestamp' in colnames:
            insert_dict['finish_timestamp'] = item._finish_timestamp

        if 'runtime' in colnames:
            runtime = item._runtime
            if len(runtime) > pypetconstants.HDF5_STRCOL_MAX_RUNTIME_LENGTH:
                #If string is too long we cut the microseconds
                runtime = runtime.split('.')[0]

            insert_dict['runtime'] = runtime

        if 'short_environment_hexsha' in colnames:
            insert_dict['short_environment_hexsha'] = item.v_environment_hexsha[0:7]


        return insert_dict

    @staticmethod
    def _all_cut_string(string, max_length, logger):
        """Cuts string data to the maximum length allowed in a pytables column
        if string is too long.

        :param string: String to be cut
        :param max_length: Maximum allowed string length
        :param logger: Logger where messages about truncating should be written

        :return: String, cut if too long

        """
        if len(string) > max_length:
            logger.debug('The string `%s` was too long I truncated it to'
                                 ' %d characters' %
                                 (string,max_length))
            string = string[0:max_length-3] + '...'

        return string

    def _all_create_or_get_groups(self, key):
        """Creates new or follows existing group nodes along a given colon separated `key`.

        :param key:

            Colon separated path along hdf5 file, e.g. `parameters.mobiles.cars`.

        :return:

            Final group node, e.g. group node with name `cars`.

        """
        newhdf5group = self._trajectory_group
        split_key = key.split('.')
        created = False
        for name in split_key:
            if not name in newhdf5group:
                try:
                    newhdf5group=self._hdf5file.create_group(where=newhdf5group, name=name,
                                                             title=name, filters=self._get_filters())
                except AttributeError:
                    newhdf5group=self._hdf5file.createGroup(where=newhdf5group, name=name,
                                                            title=name, filters=self._get_filters())
                created = True
            else:
                try:
                    newhdf5group=newhdf5group._f_get_child(name)
                except AttributeError:
                    newhdf5group=newhdf5group._f_getChild(name)

        return newhdf5group, created


    ################# Storing and loading Annotations ###########################################

    def _ann_store_annotations(self,item_with_annotations,node):
        """Stores annotations into an hdf5 file."""

        # Only store annotations if the item has some
        if not item_with_annotations.v_annotations.f_is_empty():

            anno_dict = item_with_annotations.v_annotations.__dict__

            current_attrs = node._v_attrs

            changed = False

            for field_name, val in anno_dict.iteritems():
                field_name_with_prefix = HDF5StorageService.ANNOTATION_PREFIX+field_name
                if not field_name_with_prefix in current_attrs:
                    # Only store *new* annotations, if they already exist on disk, skip storage
                    setattr(current_attrs,field_name_with_prefix,val)
                    changed = True

            if changed:
                setattr(current_attrs, HDF5StorageService.ANNOTATED,True)
                self._hdf5file.flush()


    def _ann_load_annotations(self,item_with_annotations,node):
        """Loads annotations from disk."""

        annotated = self._all_get_from_attrs(node,HDF5StorageService.ANNOTATED)

        if annotated:

            annotations =item_with_annotations.v_annotations

            # You can only load into non-empty annotations, to prevent overwriting data in RAM
            if not annotations.f_is_empty():
                raise TypeError('Loading into non-empty annotations!')

            current_attrs = node._v_attrs

            for attr_name in current_attrs._v_attrnames:

                if attr_name.startswith(HDF5StorageService.ANNOTATION_PREFIX):
                    key = attr_name
                    key=key.replace(HDF5StorageService.ANNOTATION_PREFIX,'')

                    data = getattr(current_attrs,attr_name)
                    setattr(annotations,key,data)


    ############################################## Storing Groups ################################

    def _grp_store_group(self, node_in_traj, _hdf5_group = None):
        """Stores a group node.

        For group nodes only annotations and comments need to be stored.

        """
        if _hdf5_group is None:
            _hdf5_group,_ = self._all_create_or_get_groups(node_in_traj.v_full_name)

        if node_in_traj.v_comment != '' and HDF5StorageService.COMMENT not in _hdf5_group._v_attrs:
            setattr(_hdf5_group._v_attrs, HDF5StorageService.COMMENT, node_in_traj.v_comment)

        self._ann_store_annotations(node_in_traj,_hdf5_group)

        node_in_traj._stored = True


    ################# Storing and Loading Parameters ############################################

    def _prm_extract_missing_flags(self,data_dict, flags_dict):
        """Extracts storage flags for data in `data_dict`
        if they were not specified in `flags_dict`.

        See :const:`~pypet.storageservice.HDF5StorageService.TYPE_FLAG_MAPPING`
        for how to store different types of data per default.

        """
        for key,data in data_dict.items():
            if not key in flags_dict:
                dtype = type(data)
                if dtype in HDF5StorageService.TYPE_FLAG_MAPPING:
                    flags_dict[key]=HDF5StorageService.TYPE_FLAG_MAPPING[dtype]
                else:
                    raise pex.NoSuchServiceError('I cannot store `%s`, I do not understand the'
                                                 'type `%s`.' %(key,str(dtype)))


    def _prm_meta_remove_summary(self, instance):
        """Changes a summary table entry if the current `instance` is removed from the trajectory
        and from disk.

        The number of items represented by a summary is decreased, if the
        number of items shrinks to zero the whole row is deleted.

        """
        split_name = instance.v_full_name.split('.')
        where = split_name[0]

        if where in['derived_parameters','results']:
            # There are only summaries for derived parameters and results
            creator_name = instance.v_run_branch
            if creator_name.startswith(pypetconstants.RUN_NAME):
                run_mask = pypetconstants.RUN_NAME+'X'*pypetconstants.FORMAT_ZEROS

                split_name[instance._run_branch_pos] = run_mask

                new_full_name = '.'.join(split_name)
                old_full_name = instance.v_full_name
                instance._rename(new_full_name)
                try:
                    table_name = where+'_runs_summary'
                    table = getattr(self._overview_group,table_name)

                    row_iterator= self._all_find_param_or_result_entry_and_return_iterator(instance, table)


                    row = row_iterator.next()

                    # Decrease the number of items represented by the summary
                    nitems = row['number_of_items']-1
                    row['number_of_items'] = nitems
                    row.update()

                    try:
                        row_iterator.next()
                        raise RuntimeError('There is something completely wrong, found '
                                           '`%s` twice in a table!' %
                                        instance.v_full_name)
                    except StopIteration:
                        pass


                    table.flush()

                    if nitems == 0:
                        # Here the summary became obsolete
                        self._all_store_param_or_result_table_entry(instance,table,
                                                    flags=(HDF5StorageService.REMOVE_ROW,))


                except  pt.NoSuchNodeError:
                    pass
                except StopIteration:
                    pass
                finally:
                    # Get the old name back
                    instance._rename(old_full_name)

    def _all_meta_add_summary(self, instance):
        """Adds data to the summary tables and returns if `instance`s comment has to be stored.

        Also moves comments upwards in the hierarchy if purge_duplicate_comments is true
        and a lower index run has completed. Only necessary for *multiprocessing*.

        :return: Tuple

            * String specifying the subtree

            * Boolean whether to store the comment to `instance`s hdf5 node

        """
        definitely_store_comment=True

        split_name = instance.v_full_name.split('.')
        where = split_name[0]

        # Check if we are in the subtree that has runs overview tables
        creator_name = instance.v_run_branch
        if creator_name.startswith(pypetconstants.RUN_NAME):

            try:
                # Get the overview table
                table_name = where+'_runs_summary'

                # Check if the overview table exists, otherwise skip the rest of
                # the meta adding
                if table_name in self._overview_group:
                    table = getattr(self._overview_group, table_name)
                else:
                    return where, definitely_store_comment
            except  pt.NoSuchNodeError:
                return where, definitely_store_comment

            # Create the dummy name `result.run_XXXXXXXX` as a general mask and example item
            run_mask = pypetconstants.RUN_NAME+'X'*pypetconstants.FORMAT_ZEROS

            split_name[instance._run_branch_pos] = run_mask

            new_full_name = '.'.join(split_name)
            old_full_name = instance.v_full_name
            # Rename the item for easier storage
            instance._rename(new_full_name)
            try:

                # True if comment must be moved upwards to lower index
                erase_old_comment=False

                # Find the overview table entry

                row_iterator = \
                     self._all_find_param_or_result_entry_and_return_iterator(instance, table)


                row = None
                try:
                    row = row_iterator.next()
                except StopIteration:
                    pass

                if row is not None:
                    # If row found we need to increase the number of items
                    nitems = row['number_of_items']+1

                    # Get the run name of the example
                    example_item_run_name = row['example_item_run_name']

                    # Get the old comment:
                    location_string = row['location']
                    other_parent_node_name = location_string.replace(run_mask, example_item_run_name)
                    other_parent_node_name = '/' + self._trajectory_name + '/' + \
                                             other_parent_node_name.replace('.','/')

                    # If the instance actually has the name of the run as it's own name
                    # We need this replacement as well:
                    instance_name = instance.v_name.replace(run_mask, example_item_run_name)
                    try:
                        example_item_node = self._hdf5file.get_node(where=other_parent_node_name,
                                                                               name=instance_name)
                    except AttributeError:
                        example_item_node = self._hdf5file.getNode(where=other_parent_node_name,
                                                                        name = instance_name)

                    # Check if comment is obsolete
                    example_comment = ''
                    if HDF5StorageService.COMMENT in example_item_node._v_attrs:
                        example_comment = str(example_item_node._v_attrs[HDF5StorageService.COMMENT])
                    definitely_store_comment=instance.v_comment != example_comment

                    # We can rely on lexicographic comparisons with run indices
                    if creator_name < example_item_run_name:
                        # In case the statement is true and the comments are equal, we need
                        # to move the comment to a result or derived parameter with a lower
                        # run name:
                        if not definitely_store_comment:

                            # We need to purge the comment in the other result or derived parameter
                            erase_old_comment=True
                            definitely_store_comment=True

                            row['example_item_run_name']=creator_name

                            row['value'] = self._all_cut_string(instance.f_val_to_str(),
                                                pypetconstants.HDF5_STRCOL_MAX_VALUE_LENGTH,
                                                self._logger)
                        else:
                            self._logger.warning('Your example value and comment in the overview'
                                     ' table cannot be set to the lowest index'
                                     ' item because results or derived parameters'
                                     ' with lower indices have '
                                     ' a different comment! The comment of `%s` '
                                     ' in run `%s'
                                     ' differs from the current result or'
                                     ' derived parameter in run `%s`.' %
                                       (instance.v_name, creator_name, example_item_run_name))


                    row['number_of_items'] = nitems
                    row.update()

                    try:
                        row_iterator.next()
                        raise RuntimeError('There is something completely wrong, '
                                           'found `%s` twice in a table!' %
                                        instance.v_full_name)
                    except StopIteration:
                        pass


                    table.flush()

                    if (self._purge_duplicate_comments and erase_old_comment and
                            HDF5StorageService.COMMENT in example_item_node._v_attrs):
                        del example_item_node._v_attrs[HDF5StorageService.COMMENT]

                    self._hdf5file.flush()
                    pass
                else:
                    self._all_store_param_or_result_table_entry(instance,table,
                                        flags=(HDF5StorageService.ADD_ROW,),
                                        additional_info={'example_item_run_name': creator_name})

                    definitely_store_comment=True

            #There are 2 cases of exceptions, either the table is switched off, or
            #the entry already exists, in both cases we  have to store the comments
            except  pt.NoSuchNodeError:
                definitely_store_comment=True
            finally:
                # Get the old name back
                instance._rename(old_full_name)

        return where, definitely_store_comment

    def _prm_add_meta_info(self,instance,group,msg):
        """Adds information to overview tables and meta information to the `instance`s hdf5 `group`.

        :param instance: Instance to store meta info about
        :param group: HDF5 group of instance
        :param msg: Whether to update leaf (we need to modify a row) or just store it

        """

        flags=(HDF5StorageService.ADD_ROW,)

        # Check if we need to store the comment. Maybe update the overview tables
        # accordingly if the current run index is lower than the one in the table.
        where, definitely_store_comment = self._all_meta_add_summary(instance)


        try:
            # Update the summary overview table
            table_name = self._all_get_table_name(where, instance.v_run_branch)

            table = getattr(self._overview_group,table_name)

            self._all_store_param_or_result_table_entry(instance,table,
                                                        flags=flags)
        except pt.NoSuchNodeError:
                pass


        if ((not self._purge_duplicate_comments or definitely_store_comment) and instance.v_comment != ''):
            # Only add the comment if necessary
            setattr(group._v_attrs, HDF5StorageService.COMMENT, instance.v_comment)

        # Add class name and whether node is a leaf to the HDF5 attributes
        setattr(group._v_attrs, HDF5StorageService.CLASS_NAME, instance.f_get_class_name())
        setattr(group._v_attrs, HDF5StorageService.LEAF, 1)


        if instance.v_is_parameter and instance.f_has_range():
            # If the stored parameter was an explored one we need to mark this in the
            # explored overview table
            setattr(group._v_attrs, HDF5StorageService.LENGTH, len(instance))
            try:
                tablename = 'explored_parameters'
                table = getattr(self._overview_group,tablename)
                self._all_store_param_or_result_table_entry(instance, table,
                                                        flags=flags)
            except pt.NoSuchNodeError:
                pass

    def _prm_store_parameter_or_result(self, msg, instance, store_flags=None,
                                       overwrite=None, _hdf5_group=None, _newly_created=False):
        """Stores a parameter or result to hdf5.

        :param msg:

            Either :const:`~pypet.pypetconstants.LEAF` for storing a new parameter or result

        :param instance:

            The instance to be stored

        :param store_flags:

            Dictionary containing how to store individual data, usually empty.

        :param _hdf5_group:

            The hdf5 group for storing the parameter or result

        """
        fullname = instance.v_full_name
        self._logger.debug('Storing %s.' % fullname)


        if _hdf5_group is None:
            # If no group is provided we might need to create one
            _hdf5_group, newly_created = self._all_create_or_get_groups(fullname)
        else:
            newly_created = _newly_created

        try:

            # Get the data to store from the instance
            if not instance.f_is_empty():
                store_dict = instance._store()
            else:
                store_dict = {}

            # If the user did not supply storage flags, we need to set it to the empty dictionary
            if store_flags is None:
                store_flags = {}

            try:
                # Ask the instance for storage flags
                instance_flags = instance._store_flags()
            except AttributeError:
                # If it does not provide any, set it to the empty dictionary
                instance_flags = {}

            # User specified flags have priority over the flags from the instance
            instance_flags.update(store_flags)
            store_flags=instance_flags

            # If we still have data in `store_dict` about which we do not know how to store
            # it, pick default storage flags
            self._prm_extract_missing_flags(store_dict, store_flags)

            if isinstance(overwrite, basestring):
                overwrite = [overwrite]

            if overwrite is True:
                to_delete = [key for key in store_dict.keys() if key in _hdf5_group]
                self._all_delete_parameter_or_result_or_group(instance,
                                                              delete_only=to_delete)
            elif overwrite is not None:
                overwrite_set = set(overwrite)
                key_set = set(store_dict.keys())

                stuff_not_to_be_overwritten = overwrite_set - key_set

                if len(stuff_not_to_be_overwritten) > 0:
                    self._logger.warning('Cannot overwrite `%s`, these items are not supposed to '
                                'be stored by the leaf node.' % str(stuff_not_to_be_overwritten))

                stuff_to_overwrite = overwrite_set & key_set
                if len(stuff_to_overwrite) > 0:
                    self._all_delete_parameter_or_result_or_group(instance,
                                        delete_only=list(stuff_to_overwrite))

            for key, data_to_store in store_dict.items():

                # Iterate through the data and store according to the storage flags
                if  key in _hdf5_group:
                    # We won't change any data that is found on disk
                    self._logger.debug('Found %s already in hdf5 node of %s, so I will ignore it.' %
                                       (key, fullname))
                    continue
                if store_flags[key] == HDF5StorageService.TABLE:
                    self._prm_store_into_pytable(msg, key, data_to_store, _hdf5_group, fullname)
                elif store_flags[key] == HDF5StorageService.DICT:
                    self._prm_store_dict_as_table(msg, key, data_to_store, _hdf5_group, fullname)
                elif store_flags[key] == HDF5StorageService.ARRAY:
                    self._prm_store_into_array(msg, key, data_to_store, _hdf5_group, fullname)
                elif store_flags[key] == HDF5StorageService.CARRAY:
                    self._prm_store_into_carray(msg, key, data_to_store, _hdf5_group, fullname)
                elif store_flags[key] == HDF5StorageService.FRAME:
                    self._prm_store_data_frame(msg, key, data_to_store, _hdf5_group, fullname)
                elif store_flags[key] == HDF5StorageService.SERIES:
                    self._prm_store_series(msg ,key, data_to_store, _hdf5_group, fullname)
                elif store_flags[key] == HDF5StorageService.PANEL:
                    self._prm_store_panel(msg ,key, data_to_store, _hdf5_group, fullname)
                else:
                    raise RuntimeError('You shall not pass!')

            # Store annotations
            self._ann_store_annotations(instance,_hdf5_group)

            if newly_created:
                # If we created a new group or the parameter was extended we need to
                # update the meta information and summary tables
                self._prm_add_meta_info(instance, _hdf5_group, msg)

            instance._stored=True

        except:
            # I anything fails, we want to remove the parameter again
            self._logger.error('Failed storing leaf `%s`. I will remove the hdf5 node corresponding to '
                         'the leaf again.' % fullname)
            _hdf5_group._f_remove(recursive=True)
            raise


    def _prm_store_dict_as_table(self, msg, key, data_to_store, group, fullname):
        """Stores a python dictionary as pytable

        :param msg:

            Message passed to the storage service ('LEAF')

        :param key:

            Name of data item to store

        :param data_to_store:

            Dictionary to store

        :param group:

            Group node where to store data in hdf5 file

        :param fullname:

            Full name of the `data_to_store`s original container, only needed for throwing errors.

        """
        if key in group:
            raise ValueError('Dictionary `%s` already exists in `%s`. Appending is not supported (yet).')

        if key in group:
            raise ValueError('Dict `%s` already exists in `%s`. Appending is not supported (yet).')

        # # Create a temp_dict in order not to modify the original data
        # if len(data_to_store)> ptpa.MAX_COLUMNS:
        #     dicts = [{}]
        #     count = 0
        #     for innerkey in data_to_store:
        #         val = data_to_store[innerkey]
        #         if count == ptpa.MAX_COLUMNS:
        #             dicts.append({})
        #             count = 0
        #         dicts[-1][innerkey] = val
        #         count += 1
        #     try:
        #         subgroup = self._hdf5file.create_group(where=group, name=key)
        #     except AttributeError:
        #         subgroup = self._hdf5file.createGroup(where=group, name=key)
        #
        #     setattr(subgroup._v_attrs,HDF5StorageService.STORAGE_TYPE,
        #             HDF5StorageService.DICT)
        #     setattr(subgroup._v_attrs,HDF5StorageService.DICT_SPLIT,
        #             1)
        #
        #     for idx, dictionary in enumerate(dicts):
        #         self._prm_store_dict_as_table(msg, key+'_%d' % idx, dictionary,
        #                                       subgroup, fullname)
        # else:

        temp_dict={}
        for innerkey in data_to_store:
            val = data_to_store[innerkey]
            temp_dict[innerkey] =[val]

        # Convert dictionary to object table
        objtable = ObjectTable(data=temp_dict)

        # Then store the object table
        self._prm_store_into_pytable(msg,key,objtable,group,fullname)

        try:
            new_table = group._f_get_child(key)
        except AttributeError:
            new_table = group._f_getChild(key)

        # Remember that the Object Table represents a dictionary
        self._all_set_attributes_to_recall_natives(temp_dict, new_table,
                                                   HDF5StorageService.DATA_PREFIX)

        setattr(new_table._v_attrs,HDF5StorageService.STORAGE_TYPE,
                HDF5StorageService.DICT)

        self._hdf5file.flush()


    def _prm_store_series(self, msg, key, data, group, fullname):
        """Stores a pandas Series into hdf5.

        :param msg:

            Message passed to the storage service ('LEAF')

        :param key:

            Name of data item to store

        :param data:

            DataFrame to store

        :param group:

            Group node where to store data in hdf5 file

        :param fullname:

            Full name of the `data_to_store`s original container, only needed for throwing errors.

        """
        try:

            if key in group:
                raise ValueError('Series `%s` already exists in `%s`. Appending is not supported (yet).')


            name = group._v_pathname+'/' +key
            pandas_store = self._hdf5store
            pandas_store.put(name, data)
            pandas_store.flush()
            self._hdf5file.flush()

            try:
                frame_group = group._f_get_child(key)
            except AttributeError:
                frame_group = group._f_getChild(key)

            setattr(frame_group._v_attrs,HDF5StorageService.STORAGE_TYPE, HDF5StorageService.FRAME)
            self._hdf5file.flush()
        except:
            self._logger.error('Failed storing Series `%s` of `%s`.' %(key,fullname))
            raise

    def _prm_store_panel(self, msg, key, data, group, fullname):
        """Stores a pandas Panel into hdf5.

        :param msg:

            Message passed to the storage service ('LEAF')

        :param key:

            Name of data item to store

        :param data:

            DataFrame to store

        :param group:

            Group node where to store data in hdf5 file

        :param fullname:

            Full name of the `data_to_store`s original container, only needed for throwing errors.

        """
        try:

            if key in group:
                raise ValueError('Series `%s` already exists in `%s`. Appending is not supported (yet).')


            name = group._v_pathname+'/' +key
            pandas_store = self._hdf5store
            pandas_store.put(name, data,
                             format=self.pandas_format,
                            append= self.pandas_append)
            pandas_store.flush()
            self._hdf5file.flush()

            try:
                frame_group = group._f_get_child(key)
            except AttributeError:
                frame_group = group._f_getChild(key)

            setattr(frame_group._v_attrs,HDF5StorageService.STORAGE_TYPE, HDF5StorageService.FRAME)
            self._hdf5file.flush()
        except:
            self._logger.error('Failed storing Series `%s` of `%s`.' %(key,fullname))
            raise

    def _prm_store_data_frame(self, msg,  key, data, group, fullname):
        """Stores a pandas DataFrame into hdf5.

        :param msg:

            Message passed to the storage service ('LEAF')

        :param key:

            Name of data item to store

        :param data:

            DataFrame to store

        :param group:

            Group node where to store data in hdf5 file

        :param fullname:

            Full name of the `data_to_store`s original container, only needed for throwing errors.

        """
        try:

            if key in group:
                raise ValueError('DataFrame `%s` already exists in `%s`. Appending is not supported (yet).')

            name = group._v_pathname+'/' +key
            pandas_store = self._hdf5store
            pandas_store.put(name, data,
                             format=self.pandas_format,
                            append= self.pandas_append,
                            expected_rows=data.shape[0])
            pandas_store.flush()
            self._hdf5file.flush()

            try:
                frame_group = group._f_get_child(key)
            except AttributeError:
                frame_group = group._f_getChild(key)

            setattr(frame_group._v_attrs,HDF5StorageService.STORAGE_TYPE, HDF5StorageService.FRAME)
            self._hdf5file.flush()

        except:
            self._logger.error('Failed storing DataFrame `%s` of `%s`.' %(key,fullname))
            raise

    def _prm_store_into_carray(self, msg, key, data, group, fullname):
        """Stores data as carray.

        :param msg:

            Message passed to the storage service ('LEAF').
            Not needed here.

        :param key:

            Name of data item to store

        :param data:

            Data to store

        :param group:

            Group node where to store data in hdf5 file

        :param fullname:

            Full name of the `data_to_store`s original container, only needed for throwing errors.

        """
        try:
            if key in group:
                raise ValueError('CArray `%s` already exists in `%s`. Appending is not supported (yet).')


            # # if isinstance(data, np.ndarray):
            # #     size = data.size
            # if hasattr(data,'__len__'):
            #     size = len(data)
            # else:
            #     size = 1
            #
            # if size == 0:
            #     self._logger.warning('`%s` of `%s` is _empty, I will skip storing.' %(key,fullname))
            #     return

            #try using pytables 3.0.0 API
            try:
                carray=self._hdf5file.create_carray(where=group, name=key, obj=data, filters=self._get_filters())
            except AttributeError:
                #if it does not work, create carray with old api
                atom = pt.Atom.from_dtype(data.dtype)
                carray=self._hdf5file.createCArray(where=group, name=key, atom=atom,
                                                   shape=data.shape, filters=self._get_filters())
                carray[:]=data[:]

            # Remember the types of the original data to recall them on loading
            self._all_set_attributes_to_recall_natives(data, carray, HDF5StorageService.DATA_PREFIX)
            setattr(carray._v_attrs, HDF5StorageService.STORAGE_TYPE, HDF5StorageService.CARRAY)
            self._hdf5file.flush()
        except:
            self._logger.error('Failed storing array `%s` of `%s`.' % (key, fullname))
            raise

    def _prm_store_into_array(self, msg, key, data, group, fullname):
        """Stores data as array.

        :param msg:

            Message passed to the storage service ('LEAF').
            Not needed here.

        :param key:

            Name of data item to store

        :param data:

            Data to store

        :param group:

            Group node where to store data in hdf5 file

        :param fullname:

            Full name of the `data_to_store`s original container, only needed for throwing errors.

        """
        try:
            if key in group:
                raise ValueError('Array `%s` already exists in `%s`. Appending is not supported (yet).')

            # if hasattr(data,'__len__'):
            #     size = len(data)
            # else:
            #     size = 1
            #
            # if size == 0:
            #     self._logger.warning('`%s` of `%s` is _empty, I will skip storing.' %(key,fullname))
            #     return

            try:
                array=self._hdf5file.create_array(where=group, name=key,obj=data)
            except AttributeError:
                array=self._hdf5file.createArray(where=group, name=key,object=data)

            # Remember the types of the original data to recall them on loading
            self._all_set_attributes_to_recall_natives(data ,array, HDF5StorageService.DATA_PREFIX)
            setattr(array._v_attrs,HDF5StorageService.STORAGE_TYPE, HDF5StorageService.ARRAY)
            self._hdf5file.flush()
        except:
            self._logger.error('Failed storing array `%s` of `%s`.' % (key, fullname))
            raise

    def _all_delete_parameter_or_result_or_group(self, instance,
                                                 remove_empty_groups=False,
                                                 delete_only=None,
                                                 remove_from_item=False):
        """Removes a parameter or result or group from the hdf5 file.

        :param instance: Instance to be removed

        :param remove_empty_groups: Whether to delete groups that might become empty due to deletion

        :param delete_only:

            List of elements if you only want to delete parts of a leaf node. Note that this
            needs to list the names of the hdf5 subnodes. BE CAREFUL if you erase parts of a leaf.
            Erasing partly happens at your own risk, it might be the case that you can
            no longer reconstruct the leaf from the leftovers!

        :param remove_from_item:

            If using `delete_only` and `remove_from_item=True` after deletion the data item is
            also removed from the `instance`.


        """
        split_name = instance.v_location.split('.')

        where = '/'+self._trajectory_name+'/' + '/'.join(split_name)

        node_name = instance.v_name

        if delete_only is None:

            try:
                the_node = self._hdf5file.get_node(where=where, name=node_name)
            except AttributeError:
                the_node = self._hdf5file.getNode(where=where, name=node_name)

            if not instance.v_is_leaf:
                if len(the_node._v_groups) != 0:
                    raise TypeError('You cannot remove the group `%s`, it is not empty!' %
                                    instance.v_full_name)

            if instance.v_is_leaf:
                # If we delete a leaf we need to take care about overview tables
                base_group = split_name[0]

                table_name = self._all_get_table_name(base_group, instance.v_run_branch)

                if table_name in self._overview_group:
                    table = getattr(self._overview_group, table_name)

                    self._all_store_param_or_result_table_entry(instance, table,
                                                     flags=(HDF5StorageService.REMOVE_ROW,))

                if instance.v_is_parameter:
                    table_name = 'explored_parameters'
                    if  table_name in self._overview_group:
                        table = getattr(self._overview_group, table_name)

                        self._all_store_param_or_result_table_entry(instance, table,
                                                flags=(HDF5StorageService.REMOVE_ROW,))


                self._prm_meta_remove_summary(instance)

            the_node._f_remove(recursive=True)

            if remove_empty_groups:
                for irun in reversed(range(len(split_name))):
                    where = '/'+self._trajectory_name+'/' + '/'.join(split_name[0:irun])
                    node_name = split_name[irun]
                    try:
                        act_group = self._hdf5file.get_node(where=where, name=node_name)
                    except AttributeError:
                        act_group = self._hdf5file.getNode(where=where, name=node_name)
                    if len(act_group._v_groups) == 0:
                        try:
                            self._hdf5file.remove_node(where=where,name=node_name, recursive=True)
                        except AttributeError:
                            self._hdf5file.removeNode(where=where,name=node_name, recursive=True)
                    else:
                        break
        else:
            if not instance.v_is_leaf:
                raise ValueError('You can only choose `delete_only` mode for leafs.')

            if isinstance(delete_only, basestring):
                delete_only = [delete_only]

            path_to_leaf = where+'/'+node_name
            for delete_item in delete_only:
                if (remove_from_item and
                    hasattr(instance, '__contains__') and
                    hasattr(instance, '__delattr__') and
                    delete_item in instance):

                    delattr(instance, delete_item)
                try:
                    try:
                        the_node = self._hdf5file.get_node(where= path_to_leaf, name=delete_item)
                    except AttributeError:
                        the_node = self._hdf5file.getNode(where= path_to_leaf, name=delete_item)

                    the_node._f_remove(recursive=True)
                except pt.NoSuchNodeError:
                    self._logger.warning('Could not delete `%s` from `%s`. HDF5 node not found!' %
                                         (delete_item, instance.v_full_name))


    def _prm_store_into_pytable(self, msg, tablename, data, hdf5group, fullname):
        """Stores data as pytable.

        :param msg:

            Message passed to the storage service ('LEAF').

        :param tablename:

            Name of the data table

        :param data:

            Data to store

        :param hdf5group:

            Group node where to store data in hdf5 file

        :param fullname:

            Full name of the `data_to_store`s original container, only needed for throwing errors.

        """

        datasize = data.shape[0]

        try:

            # Get a new pytables description from the data and create a new table
            description_dict, data_type_dict = self._prm_make_description(data, fullname)
            description_dicts = [{}]

            if len(description_dict) > pypetconstants.HDF5_MAX_OBJECT_TABLE_TYPE_ATTRS:
                # For optimzation we want to store the original data types into another table
                try:
                    new_table_group=self._hdf5file.create_group(where=hdf5group, name=tablename)
                except AttributeError:
                    new_table_group=self._hdf5file.createGroup(where=hdf5group, name=tablename)
                if len(description_dict) > ptpa.MAX_COLUMNS:
                    # For further optimization we need to split the table into several
                    count = 0
                    for innerkey in description_dict:
                        val = description_dict[innerkey]
                        if count == ptpa.MAX_COLUMNS:
                            description_dicts.append({})
                            count = 0
                        description_dicts[-1][innerkey] = val
                        count += 1
                else:
                    description_dicts=[description_dict]

                setattr(new_table_group._v_attrs, HDF5StorageService.STORAGE_TYPE,
                    HDF5StorageService.TABLE)
                setattr(new_table_group._v_attrs, HDF5StorageService.SPLIT_TABLE, 1)

                hdf5group=new_table_group
            else:
                description_dicts=[description_dict]

            for idx, descr_dict in enumerate(description_dicts):

                if idx == 0:
                    tblname = tablename
                else:
                    tblname = tablename +'_%d' % idx

                try:
                    table = self._hdf5file.create_table(where=hdf5group, name=tblname,
                                                       description=descr_dict,
                                                       title=tblname,
                                                       expectedrows=datasize,
                                                       filters=self._get_filters())
                except AttributeError:
                    table = self._hdf5file.createTable(where=hdf5group, name=tblname,
                                                       description=descr_dict,
                                                       title=tblname,
                                                       expectedrows=datasize,
                                                       filters=self._get_filters())

                row = table.row
                for n in range(datasize):
                    # Fill the columns with data, note if the parameter was extended nstart!=0

                    for key in descr_dict:

                        row[key] = data[key][n]

                    row.append()


                # Remember the original types of the data for perfect recall
                if idx == 0 and len(description_dict) <= pypetconstants.HDF5_MAX_OBJECT_TABLE_TYPE_ATTRS:
                    # We only have a single table and we can store the original data types as attributes
                    for field_name, type_description in data_type_dict.iteritems():
                        table._f_setAttr(field_name,type_description)

                    setattr(table._v_attrs, HDF5StorageService.STORAGE_TYPE, HDF5StorageService.TABLE)

                table.flush()
                self._hdf5file.flush()

            if len(description_dict) > pypetconstants.HDF5_MAX_OBJECT_TABLE_TYPE_ATTRS:
                # We have potentially many split tables and the data types are
                # stored into an additional table for performance reasons
                tblname = tablename + '__' + HDF5StorageService.STORAGE_TYPE
                field_names, data_types = zip(*data_type_dict.items())
                data_type_table_dict = {'field_name' : field_names, 'data_type':data_types}
                descr_dict, _ = self._prm_make_description(data_type_table_dict, fullname)
                try:
                    table = self._hdf5file.create_table(where=hdf5group, name=tblname,
                                                       description=descr_dict,
                                                       title=tblname,
                                                       expectedrows=len(field_names),
                                                       filters=self._get_filters())
                except AttributeError:
                    table = self._hdf5file.createTable(where=hdf5group, name=tblname,
                                                       description=descr_dict,
                                                       title=tblname,
                                                       expectedrows=len(field_names),
                                                       filters=self._get_filters())

                row = table.row

                for n in range(len(field_names)):
                    # Fill the columns with data, note if the parameter was extended nstart!=0

                    for key in data_type_table_dict:

                        row[key] = data_type_table_dict[key][n]

                    row.append()

                setattr(table._v_attrs, HDF5StorageService.DATATYPE_TABLE, 1)

                table.flush()
                self._hdf5file.flush()

        except:
            self._logger.error('Failed storing table `%s` of `%s`.' %(tablename,fullname))
            raise

    def _prm_make_description(self, data, fullname):
        """ Returns a description dictionary for pytables table creation"""

        def _convert_lists_and_tuples(series_of_data):
            """Converts lists and tuples to numpy arrays"""
            if isinstance(series_of_data[0], (list, tuple)):# and not isinstance(series_of_data[0], np.ndarray):
                 # If the first data item is a list, the rest must be as well, since
                # data has to be homogeneous
                for idx,item in enumerate(series_of_data):
                    series_of_data[idx] = np.array(item)

        descriptiondict={} # dictionary containing the description to build a pytables table
        original_data_type_dict={} # dictionary containing the original data types

        for key, val in data.iteritems():

            # remember the original data types
            self._all_set_attributes_to_recall_natives(val[0], PTItemMock(original_data_type_dict),
                            HDF5StorageService.FORMATTED_COLUMN_PREFIX % key)

            _convert_lists_and_tuples(val)

            # get a pytables column from the data
            col = self._prm_get_table_col(key, val, fullname)

            descriptiondict[key]=col

        return descriptiondict, original_data_type_dict

    def _prm_get_table_col(self, key, column, fullname):
        """ Creates a pytables column instance.

        The type of column depends on the type of `column[0]`.
        Note that data in `column` must be homogeneous!

        """
        val = column[0]

        try:

            ## We do not want to loose int_
            if type(val) is int:
                return pt.IntCol()

            if isinstance(val,str):
                itemsize = int(self._prm_get_longest_stringsize(column))
                return pt.StringCol(itemsize)

            if isinstance(val, np.ndarray):
                if np.issubdtype(val.dtype,np.str):
                    itemsize = int(self._prm_get_longest_stringsize(column))
                    return pt.StringCol(itemsize,shape=val.shape)
                else:
                    return pt.Col.from_dtype(np.dtype((val.dtype,val.shape)))
            else:
                return pt.Col.from_dtype(np.dtype(type(val)))
        except Exception:
            self._logger.error('Failure in storing `%s` of Parameter/Result `%s`.'
                               ' Its type was `%s`.' % (key,fullname,repr(type(val))))
            raise

    @staticmethod
    def _prm_get_longest_stringsize(string_list):
        """ Returns the longest string size for a string entry across data."""
        maxlength = 1

        for stringar in string_list:
            if not isinstance(stringar,np.ndarray) or stringar.ndim==0:
                stringar = np.array([stringar])

            for string in stringar:
                maxlength = max(len(string),maxlength)

        # Make the string Col longer than needed in order to allow later on slightly larger strings
        return maxlength*1.5

    def _prm_load_parameter_or_result(self, param, load_only=None, load_except=None,
                                      _hdf5_group=None):
        """Loads a parameter or result from disk.

        :param param:

            Empty parameter or result instance

        :param load_only:

            List of data keys if only parts of a result should be loaded

        :param load_except:

            List of data key that should NOT be loaded.

        :param _hdf5_group:

            The corresponding hdf5 group of the instance

        """

        if load_only is not None and load_except is not None:
            raise ValueError('Please use either `load_only` or `load_except` and not '
                             'both at the same time.')

        # If load only is just a name and not a list of names, turn it into a 1 element list
        if isinstance(load_only, basestring):
            load_only= [load_only]
        if isinstance(load_except, basestring):
            load_except = [load_except]


        if load_only is not None:
            self._logger.debug('I am in load only mode, I will only load %s.' %
                                   str(load_only))
            load_only = set(load_only)
        elif load_except is not None:
            self._logger.debug('I am in load except mode, I will load everything except %s.' %
                                   str(load_except))
            # We do not want to modify the original list
            load_except = set(load_except)


        if _hdf5_group is None:
            _hdf5_group = self._all_get_node_by_name(param.v_full_name)

        full_name = param.v_full_name

        self._logger.debug('Loading %s' % full_name)

        load_dict = {} # Dict that will be used to keep all data for loading the parameter or
                       # result

        for node in _hdf5_group:

            if load_only is not None:

                if node._v_name not in load_only:
                    continue
                else:
                    load_only.remove(node._v_name)

            elif load_except is not None:
                if node._v_name in load_except:
                    load_except.remove(node._v_name)
                    continue

            # Recall from the hdf5 node attributes how the data was stored and reload accordingly
            load_type = self._all_get_from_attrs(node, HDF5StorageService.STORAGE_TYPE)

            if load_type == HDF5StorageService.DICT:
                self._prm_read_dictionary(node, load_dict, full_name)
            elif load_type == HDF5StorageService.TABLE:
                self._prm_read_table(node, load_dict, full_name)
            elif load_type in [HDF5StorageService.ARRAY, HDF5StorageService.CARRAY]:
                self._prm_read_array(node, load_dict, full_name)
            elif load_type in [HDF5StorageService.FRAME,
                               HDF5StorageService.SERIES,
                               HDF5StorageService.PANEL]:
                self._prm_read_pandas(node, load_dict, full_name)
            else:
                raise pex.NoSuchServiceError('Cannot load %s, do not understand the hdf5 file '
                                             'structure of %s [%s].' %
                                             (full_name, str(node),str(load_type)) )


        if load_only is not None:
            # Check if all data in `load_only` was actually found in the hdf5 file
            if len(load_only) > 0:
                self._logger.warning('You marked %s for load only, '
                                     'but I cannot find these for `%s`' %
                                 (str(load_only),full_name) )
        elif load_except is not None:
            if len(load_except) > 0:
                self._logger.warning(('You marked `%s` for not loading, but these were not part '
                                      'of `%s` anyway.' % (str(load_except), full_name)))

        # Finally tell the parameter or result to load the data, if there was any ;-)
        if load_dict:
            try:
                param._load(load_dict)
            except:
                # If there happens to be any exception on loading, we want to empty the parameter
                # again. This is especially important if the user hits Ctrl-C, otherwise he
                # would end up with a half-loaded leaf which needs to be manually erased and
                # reloaded.
                self._logger.error('Error while reconstructing data of leaf `%s`. I will empty the '
                             'leaf again!' % full_name)
                param.f_empty()
                # ...And be nice and reraise the error
                raise


    def _prm_read_dictionary(self, leaf, load_dict, full_name):
        """Loads data that was originally a dictionary when stored

        :param leaf:

            PyTables table containing the dictionary data

        :param load_dict:

            Dictionary to keep the loaded data in

        :param full_name:

            Full name of the parameter or result whose data is to be loaded

        """
        try:
            # if self._all_get_from_attrs(leaf, HDF5StorageService.DICT_SPLIT):
            #     temp_dict = {}
            #     children = leaf._v_children
            #     for tablename in children:
            #         table = children[tablename]
            #         self._prm_read_dictionary(table, temp_dict, full_name)
            #     key =leaf._v_name
            #     load_dict[key]={}
            #     for dictname in temp_dict:
            #         dictionary = temp_dict[dictname]
            #         load_dict[key].update(dictionary)
            # else:
            temp_dict={}
            # Load as Pbject Table
            self._prm_read_table(leaf, temp_dict,full_name)
            key =leaf._v_name
            temp_table = temp_dict[key]
            # Turn the ObjectTable into a dictionary of lists (with length 1).
            temp_dict = temp_table.to_dict('list')

            innder_dict = {}
            load_dict[key] = innder_dict

            # Turn the dictionary of lists into a normal dictionary
            for innerkey, vallist in temp_dict.items():
                innder_dict[innerkey] = vallist[0]
        except:
            self._logger.error('Failed loading `%s` of `%s`.' % (leaf._v_name,full_name))
            raise


    def _prm_read_pandas(self,pd_node, load_dict, full_name):
        """Reads a DataFrame from dis.

        :param pd_node:

            hdf5 node stroing the pandas DataFrame

        :param load_dict:

            Dictionary to keep the loaded data in

        :param full_name:

            Full name of the parameter or result whose data is to be loaded

        """
        try:
            name = pd_node._v_name
            pathname = pd_node._v_pathname
            pandas_store = self._hdf5store
            pandas_data = pandas_store.get(pathname)
            load_dict[name] = pandas_data
        except:
            self._logger.error('Failed loading `%s` of `%s`.' % (pd_node._v_name,full_name))
            raise

    def _prm_read_table(self, table_or_group, load_dict, full_name):
        """Reads a non-nested PyTables table column by column and created a new ObjectTable for
        the loaded data.

        :param table_or_group:

            PyTables table to read from or a group containing subtables.

        :param load_dict:

            Dictionary where the loaded ObjectTable will be kept

        :param full_name:

            Full name of the parameter or result whose data is to be loaded

        """
        try:
            if self._all_get_from_attrs(table_or_group, HDF5StorageService.SPLIT_TABLE):
                table_name = table_or_group._v_name
                
                data_type_table_name = table_name + '__' + HDF5StorageService.STORAGE_TYPE

                data_type_table = table_or_group._v_children[data_type_table_name]
                data_type_dict = {}
                for row in data_type_table:
                    fieldname = str(row['field_name'])
                    data_type_dict[fieldname]= str(row['data_type'])
                
                for sub_table in table_or_group:
                    sub_table_name = sub_table._v_name
                    
                    if sub_table_name == data_type_table_name:
                        continue

                    for colname in sub_table.colnames:
                        # Read Data column by column
                        col = sub_table.col(colname)
                        data_list=list(col)

                        prefix = HDF5StorageService.FORMATTED_COLUMN_PREFIX % colname
                        for idx,data in enumerate(data_list):
                            # Recall original type of data
                            data,type_changed = self._all_recall_native_type(data,
                                                        PTItemMock(data_type_dict), prefix)
                            if type_changed:
                                data_list[idx] = data
                            else:
                                break

                        # Construct or insert into an ObjectTable
                        if table_name in load_dict:
                            load_dict[table_name][colname] = data_list
                        else:
                            load_dict[table_name] = ObjectTable(data={colname:data_list})

            else:

                table_name = table_or_group._v_name

                for colname in table_or_group.colnames:
                    # Read Data column by column
                    col = table_or_group.col(colname)
                    data_list=list(col)

                    prefix = HDF5StorageService.FORMATTED_COLUMN_PREFIX % colname
                    for idx,data in enumerate(data_list):
                        # Recall original type of data
                        data,type_changed = self._all_recall_native_type(data, table_or_group, prefix)
                        if type_changed:
                            data_list[idx] = data
                        else:
                            break

                    # Construct or insert into an ObjectTable
                    if table_name in load_dict:
                        load_dict[table_name][colname] = data_list
                    else:
                        load_dict[table_name] = ObjectTable(data={colname:data_list})
        except:
            self._logger.error('Failed loading `%s` of `%s`.' % (table_or_group._v_name,full_name))
            raise


    def _prm_read_array(self, array, load_dict, full_name):
        """Reads data from an array or carray

        :param array:

            PyTables array or carray to read from

        :param load_dict:

            Dictionary where the loaded ObjectTable will be kept

        :param full_name:

            Full name of the parameter or result whose data is to be loaded
        """
        try:
            result = array.read()
            # Recall original data types
            result, dummy = self._all_recall_native_type(result,array,HDF5StorageService.DATA_PREFIX)

            load_dict[array._v_name]=result
        except:
            self._logger.error('Failed loading `%s` of `%s`.' % (array._v_name,full_name))
            raise
