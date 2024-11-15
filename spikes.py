import copy

import numpy as np


class SpikeData:
    """Multi-input spike sequence.

    Stores a sequence of spikes defined as a list of (index, time) pairs.

    Attributes
    ----------
    spikes: dict
        Dict. containing the spike data. each key is the label for a spike
        index. The corresponding value is the list of times at whih that index
        contains spikes.
    label: str
        Descriptive name for the spike object
    n_timesteps: int
        The total number of timesteps for which the object contains info.
    """
    spikes: dict
    label: str
    n_timesteps: int

    def __init__(self, spikes:dict={}, label:str='', n_timesteps:int=-1):
        """
        Parameters
        ----------
        spikes: dict[str,list[int|float]], optional
            dictionary containing spike times for initializing the spikedata
        label: str, optional
            Descriptive name for the spike object
        n_timesteps: int, optional
            Specifies duration of the spike data. If not supplied, will be set
            to the maximum spike time plus one.
        """
        self.set_spikes(spikes, label, n_timesteps)

    def add(
        self,
        spike_data,
    ):
        """Add spike information from spike_data to the SpikeData object.

        If they share any indices, all spikes from both sets will be included
        (without duplicating times). Any detectors in spike_data not found in
        self will be added to self. Any detectors in self not found in
        spike_data are left alone. n_timesteps will be set to the larger of the
        two values. Label is left alone.

        Parameters
        ----------
        spike_data: SpikeData
            Another SpikeData object containing the spike information to add.
        """
        for label, spike_times in spike_data.get_spikes().items():
            if label in self.spikes:
                self.spikes[label] = sorted(
                    set(self.spikes[label] + spike_times)
                )
            else:
                self.spikes[label] = spike_times

        self.n_timesteps = np.max([self.n_timesteps, spike_data.n_timesteps])

        return self

    def set_spikes(
        self,
        spikes: dict,
        label: str='',
        n_timesteps: int = -1,
    ):
        """Sets the information for a spike raster, overwriting existing data.

        See initialization of class for more info.
        """
        self.spikes = copy.deepcopy(spikes)
        self.label = label

        max_timestep = max(
            [t for spike_times in self.spikes.values() for t in spike_times],
            default=0
        )

        # if n_timesteps < 0, use max_timestep + 1
        if n_timesteps < 0:
            self.n_timesteps = max_timestep + 1
        # if n_timesteps >= max_timestep, use n_timesteps
        elif n_timesteps > max_timestep:
            self.n_timesteps = n_timesteps
        # if 0 < n_timesteps <= max_timestep, use max_timestep + 1, trim spikes
        elif n_timesteps <= max_timestep:
            self.n_timesteps = max_timestep + 1
            self.spikes = self.get_spikes(0, max_timestep)

    def get_spikes(
        self,
        t_min:int=0, t_max:int=-1, relative_times=False,
        detectors:list=[]
    ):
        """Get spikes for specified detectors between t_min and t_max.

        Default is to return all spikes for all detectors.

        Parameters
        ----------
        t_min: int, optional
            Minimum time for which to return spikes
        t_max: int, optional
            Maximum time for which to return spikes
        relative_times: bool, optional
            If true, return spike times relative to `t_min`
        detectors: list[str], optional
            Names of the detectors/indices for which to return spike data.

        Returns
        -------
        spike_data: dict
            Dict containing spike data for the specified detectors/indices and
            times
        """
        # set t_max to end of data if none provided
        if t_max <= 0:
            t_max = self.n_timesteps

        # get times relative to either t_min or the beginning of the data (0)
        if relative_times:
            t_start = t_min
        else:
            t_start = 0

        # use all detectors if none provided
        if not detectors:
            detectors = list(self.spikes.keys())

        return {
            det_id: [
                t - t_start 
                for t in self.spikes[det_id]
                if t_min <= t <= t_max
            ]
            for det_id in detectors
        }

    def raster(self, key:dict={}):
        """Return the spike raster as list of lists of spike times.

        If key is provided, will use this for
        determining detector order. A key with only a subset of the detectors
        will create a raster for only those detectors.

        Parameters
        ----------
        key: dict, optional
            dictionary containing integer keys with values corresponding to
            detector/index names, used to specify the order of raster.

        Returns
        -------
        raster: list
            Nested list of spike times
        """
        if not key:
            key = {
                idx: det_id for idx, det_id in enumerate(self.spikes.keys())
            }

        return [
            self.spikes[key[idx]]
            for idx in range(len(key))
        ]

    def array(self, key:dict={}):
        """Return the spike data as a binary array.

        Array has shape (n_indices, n_timesteps). If key is provided, will use 
        this for determining detector order. A key with only a subset of the
        detectors will create a spike array for only those detectors.

        Parameters
        ----------
        key: dict, optional
            dict containing integer keys with values corresponding to detectors
            / indices. Defines the order of the array rows.

        Returns
        -------
        spike_array: numpy.ndarray
            Array of shape (n_indices, n_timesteps) containing binary spike
            data. spike_array[idx, t] = 1 corresponds to a spike occurring
            from index idx at time t.
        """
        if not key:
            key = {
                idx: det_id for idx, det_id in enumerate(self.spikes.keys())
            }

        spike_arr = np.zeros(shape=(len(key), self.n_timesteps), dtype=int)
        for idx, det_id in key.items():
            for time in self.spikes[det_id]:
                spike_arr[idx, time] = 1

        return spike_arr

    def get_spike_wheres(self):
        """Return the spike data in a format similar to np.where output.

        Returns
        -------
        (indices, times): tuple
            tuple containing a list of indices, followed by a list of
            corresponding spike times.
        """
        indices = []
        times = []
        for idx, idx_times in enumerate(self.raster()):
            for time in idx_times:
                indices.append(idx)
                times.append(time)

        return indices, times

    @classmethod
    def from_np_where(
        cls,
        indices,
        times,
        index_key=None,
        label='',
        n_timesteps=-1
    ):
        """Create SpikeData object from indices and times, as returned
        by np.where

        Parameters
        ----------
        indices: list
            list of index values for the input spikes
        times: list
            list of time values for the input spikes
        index_key: dict, optional
            key containing names for the spike indices
        label: str, optional
            Descriptive name for the spike object
        n_timesteps: int, optional
            Number of timesteps described by the spike object
        """
        if index_key is None:
            if len(indices) == 0:
                index_key = {}
            else:
                index_key = {i: i for i in range(max(indices) + 1)}
        # create spike dictionary
        spikes = {key: [] for key in index_key.values()}
        for idx, time in zip(indices, times):
            # get key using the index key and add spike time
            spikes[index_key[idx]].append(time)

        # create SpikeData object
        obj = cls()
        obj.set_spikes(spikes, label, n_timesteps)
        return obj

    @classmethod
    def from_array(
        cls,
        spike_array,
        index_key=None,
        label='',
        n_timesteps=-1
    ):
        """Create SpikeData object from a spike array.

        The array must be a 2-D array with dimensions (indices, timesteps).
        Assumes zero-valued elements are non-spikes and non-zero elements are
        spikes.

        Parameters
        ----------
        spike_array: numpy.ndarray
            Array containing spike data.
        index_key: dict, optional
            Dictionary containing labels for the indices / rows of the array
        label: str, optional
            Descriptive name for the returned SpikeData object
        n_timesteps: int, optional
            Specify a duration of time for which the object contains info.
            If not supplied, n_timesteps = spike_array.shape[1] + 1.
        """
        if index_key is None:
            index_key = {
                i: i for i in range(spike_array.shape[0])
            }
        # create spike dictionary
        spikes = {key: [] for key in index_key.values()}
        for idx, time in zip(*np.where(spike_array)):
            # get key using the index key and add spike time
            spikes[index_key[idx]].append(time)

        # create SpikeData object
        obj = cls()
        obj.set_spikes(spikes, label, n_timesteps)
        return obj

    @classmethod
    def from_sequence(
        cls,
        spike_sequence,
        index_key=None,
        label='',
        n_timesteps=-1,
    ):
        """Create SpikeData object from a sequence of spikes.

        Parameters
        ----------
        spike_sequence: list
            List of spike in the form
            [(idx0, time0), (idx1, time1), ... (idxn, timen)]
        index_key: dict, optional
            Dictionary containing labels for the indices / rows of the array
        label: str, optional
            Descriptive name for the returned SpikeData object
        n_timesteps: int, optional
            Specify a duration of time for which the object contains info.
            If not supplied, n_timesteps = spike_array.shape[1] + 1.
        """
        if index_key is None:
            # make index using detector indices of the spikes
            index_key = {
                i: i 
                for i in range(max(spike_sequence, key=lambda x:x[0])[0] + 1)
            }

        # create spike dictionary
        spikes = {key: [] for key in index_key.values()}
        for idx, time in spike_sequence:
            # get key using the index key and add spike time
            spikes[index_key[idx]].append(time)

        # create SpikeData object
        obj = cls()
        obj.set_spikes(spikes, label, n_timesteps)
        return obj


def combine_spike_data(
    x: SpikeData, y: SpikeData, n_timesteps:int=-1, label:str=''
) -> SpikeData:
    """Combine two SpikeData objects.

    Shared indices will use timesteps from both objects, without duplicating 
    repeated times. Unique indices will be added to the output object.
    Unless otherwise specified, n_timesteps is chosen as the higher of the
    two objects' n_timesteps and label is set as x.label

    Parameters
    ----------
    x, y: SpikeData
        SpikeData objects to be combined
    label: str, optional
        Descriptive name for the returned SpikeData object
    n_timesteps: int, optional
        Specify a duration of time for which the object contains info.

    Returns
    -------
    spikes: SpikeData
        combination of x and y
    """
    out = SpikeData()
    out.add(x)
    out.add(y)

    if n_timesteps > 0:
        out.n_timesteps = n_timesteps
    else:
        out.n_timesteps = np.max([x.n_timesteps, y.n_timesteps])
    
    if label:
        out.label = label
    else:
        out.label = x.label

    return out
