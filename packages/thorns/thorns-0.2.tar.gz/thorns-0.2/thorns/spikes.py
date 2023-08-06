#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Contains `spike_trains` creation and manipulation functions.

`spike_trains` is a data format to contain physiological action
potentials data and meta information.  It is based on `pd.DataFrame`,
which MUST contain two columns *spikes* and *duration*.  The values in
*spikes* are numpy arrays of spike timings in seconds.  The values in
the *duration* column are the durations of the stimuli also in
seconds.

"""

from __future__ import division, print_function, absolute_import

__author__ = "Marek Rudnicki"

import random
import numpy as np
import pandas as pd
import sys

from collections import Iterable

from thorns.stats import get_duration




def select_trains(spike_trains, **kwargs):

    mask = np.ones(len(spike_trains), dtype=bool)
    for key,val in kwargs.items():
        mask = mask & np.array(spike_trains[key] == val)

    selected = spike_trains[mask]

    return selected


select_spike_trains = select_trains
select = select_trains
sel = select_trains





def make_trains(data, **kwargs):
    if 'fs' in kwargs:
        assert 'duration' not in kwargs


    meta = dict(kwargs)

    if 'fs' in meta:
        del meta['fs']


    if isinstance(data, np.ndarray) and (data.ndim == 2) and ('fs' in kwargs):
        trains = _array_to_trains(data, kwargs['fs'], **meta)

    elif isinstance(data, dict): # brian like spiketimes (dict of arrays)
        # TODO: test this case
        arrays = [a for a in data.itervalues()]
        trains = _arrays_to_trains(arrays, **meta)

    elif ('brian' in sys.modules) and isinstance(data, sys.modules['brian'].SpikeMonitor):
        meta.setdefault('duration', float(data.clock.t))

        spikes = [spks for spks in data.spiketimes.itervalues()]
        trains = _arrays_to_trains(spikes, **meta)

    elif isinstance(data[0], Iterable):
        trains = _arrays_to_trains(data, **meta)

    else:
        raise RuntimeError("Spike train format not supported.")


    return trains





def _arrays_to_trains(arrays, **meta):
    """Convert a list of arrays with spike times to `spike trains'"""


    ### Make sure we have duration
    if 'duration' not in meta:
        max_spikes = [np.max(a) for a in arrays if len(a)>0]
        if max_spikes:
            duration = np.max(max_spikes)
        else:
            duration = 0
        meta['duration'] = float(duration)

    else:
        if np.isscalar(meta['duration']):
            meta['duration'] = float(meta['duration'])
        else:
            meta['duration'] = np.array(meta['duration']).astype(float)


    trains = {'spikes': [np.array(a) for a in arrays]}
    trains.update(meta)

    trains = pd.DataFrame(trains)

    return trains





def _array_to_trains(array, fs, **meta):
    """Convert time functions to a list of spike trains.

    fs: samping frequency in Hz
    a: input array

    return: spike trains with spike timings

    """
    assert array.ndim == 2

    trains = []
    for a in array.T:
        a = a.astype(int)
        t = np.arange(len(a))
        spikes = np.repeat(t, a) / fs

        trains.append( spikes )


    assert 'duration' not in meta

    meta['duration'] = len(array)/fs

    spike_trains = _arrays_to_trains(
        trains,
        **meta
    )

    return spike_trains





def trains_to_array(spike_trains, fs):
    """Convert spike trains to signals."""

    duration = get_duration(spike_trains)

    nbins = np.ceil(duration * fs)
    tmax = nbins / fs

    signals = []
    for spikes in spike_trains['spikes']:
        signal, bin_edges = np.histogram(
            spikes,
            bins=nbins,
            range=(0, tmax)
        )
        signals.append(
            signal
        )

    signals = np.array(signals).T

    return signals






def accumulate_spike_trains(spike_trains, ignore=None, keep=None):

    """Concatenate spike trains with the same meta data. Trains will
    be sorted by the metadata.

    """

    assert None in (ignore, keep)

    keys = spike_trains.columns.tolist()

    if ignore is not None:
        for k in ignore:
            keys.remove(k)

    if keep is not None:
        keys = keep

    if 'duration' not in keys:
        keys.append('duration')

    if 'spikes' in keys:
        keys.remove('spikes')


    groups = spike_trains.groupby(keys, as_index=False)

    acc = []
    for name,group in groups:
        if not isinstance(name, tuple):
            name = (name,)
        spikes = np.concatenate(tuple(group['spikes']))
        acc.append(name + (spikes,))

    columns = list(keys)
    columns.append('spikes')

    acc = pd.DataFrame(acc, columns=columns)

    return acc


accumulate_spikes = accumulate_spike_trains
accumulate_trains = accumulate_spike_trains
accumulate = accumulate_spike_trains




def trim_spike_trains(spike_trains, start, stop):
    """Remove all spikes outside of the (start, stop) range."""

    tmin = start

    if stop is None:
        tmaxs = spike_trains['duration']
    else:
        tmaxs = np.ones(len(spike_trains)) * stop


    assert np.all(tmin < tmaxs)


    trimmed = []
    for train,tmax in zip(spike_trains['spikes'], tmaxs):
        spikes = train[(train >= tmin) & (train <= tmax)]
        spikes -= tmin

        trimmed.append(spikes)


    durations = np.array(spike_trains['duration'])
    durations[ durations>tmaxs ] = tmaxs[ durations>tmaxs ]
    durations -= tmin


    out = spike_trains.copy()
    out['spikes'] = trimmed
    out['duration'] = durations


    return out




trim = trim_spike_trains
trim_trains = trim_spike_trains


# def remove_empty(spike_trains):
#     new_trains = []
#     for train in spike_trains:
#         if len(train) != 0:
#             new_trains.append(train)
#     return new_trains



def fold_spike_trains(spike_trains, period):
    """Fold the spike trains.

    >>> from thorns import arrays_to_trains
    >>> a = [np.array([1,2,3,4]), np.array([2,3,4,5])]
    >>> spike_trains = arrays_to_trains(a, duration=9)
    >>> fold_spike_trains(spike_trains, 3)
    [array([1, 2]), array([0, 1]), array([2]), array([0, 1, 2])]

    # >>> spike_trains = [np.array([2.]), np.array([])]
    # >>> fold_spike_trains(spike_trains, 2)
    # [array([], dtype=float64), array([ 0.]), array([], dtype=float64), array([], dtype=float64)]

    """
    # data = {key:[] for key in spike_trains.dtype.names}

    rows = []
    for i,row in spike_trains.iterrows():
        period_num = int( np.ceil(row['duration'] / period) )
        last_period = np.fmod(row['duration'], period)

        spikes = row['spikes']
        for idx in range(period_num):
            lo = idx * period
            hi = (idx+1) * period
            sec = spikes[(spikes>=lo) & (spikes<hi)]
            sec = np.fmod(sec, period)

            r = row.copy()
            r['spikes'] = sec
            r['duration'] = period

            rows.append(r)

        if last_period > 0:
            rows[-1]['duration'] = last_period


    folded_trains = pd.DataFrame(rows)
    folded_trains = folded_trains.reset_index(drop=True)

    return folded_trains


fold = fold_spike_trains
fold_trains = fold_spike_trains



# def concatenate_spikes(spike_trains):
#     return [np.concatenate(tuple(spike_trains))]

# concatenate = concatenate_spikes
# concat = concatenate_spikes


# def shift_spikes(spike_trains, shift):
#     shifted = [train+shift for train in spike_trains]

#     return shifted

# shift = shift_spikes


# def split_and_fold_trains(spike_trains,
#                           silence_duration,
#                           tone_duration,
#                           pad_duration,
#                           remove_pads):
#     silence = trim(spike_trains, 0, silence_duration)


#     tones_and_pads = trim(spike_trains, silence_duration)
#     tones_and_pads = fold(tones_and_pads, tone_duration+pad_duration)

#     # import plot
#     # plot.raster(tones_and_pads).show()

#     if remove_pads:
#         tones_and_pads = trim(tones_and_pads, 0, tone_duration)

#     return silence, tones_and_pads

# split_and_fold = split_and_fold_trains
