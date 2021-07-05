import nixio as nix
import glob
import os
import numpy as np
import matplotlib.mlab as mlab
import pandas
import math
import matplotlib.pyplot as plt
from IPython import embed
from detect_eod import detect_eod_times
from scipy.optimize import curve_fit
from scipy import signal


def jar_fit_function(t1, a1, a2, tau1, tau2):
    r = (a1 * (1 - np.exp(-t1/tau1))) + (a2 * (1 - np.exp(-t1/tau2)))
    r[t1 < 0] = 0
    return r


def jar_fit_function2(t1, a1, tau1):
    r = (a1 * (1 - np.exp(-t1/tau1)))
    r[t1 < 0] = 0
    return r


def norm_data(data, time, onset, offset):
    base = np.median(data[time < onset])
    ground = data - base

    jar = np.median(ground[(time <= offset) & (time > (onset+10.0))])
    norm = ground / jar
    return norm


def mean_traces_data(data, time, start, stop, timespan):
    # determine shortest time array
    minimum_t = min([len(time[k]) for k in range(len(time))])

    # arranging new time array
    tnew = np.arange(start, stop, timespan/minimum_t)

    # arranging new data array with all traces
    data_frame = np.zeros((len(data), len(tnew)))
    for k in range(len(data)):  # evtl. -1
        data_time = time[k]
        data_new = data[k]
        data_frame[k, :] = np.interp(tnew, data_time, data_new)

    mean_data = np.mean(data_frame, axis=0)
    return mean_data, tnew


def threshold_crossing(data, time, threshold):
    cdata = np.roll(data, 1)
    times = time[(data > threshold) & (cdata <= threshold)]
    return times


def filter_data(data, n):
    """
    :param data: raw data
    :param n: number of datapoints the mean gets computed over
    :return: filtered data
    """
    cutf = np.zeros(len(data))
    for k in np.arange(0, len(data) - n):
        kk = int(k)
        f = np.mean(data[kk:kk+n])
        kkk = int(kk+n / 2)
        if k == 0:
            cutf[:kkk] = f
        cutf[kkk] = f
    cutf[kkk:] = f
    return cutf


def detect_eod_frequency(time, trace):
    threshold = np.mean(trace) - np.mean(trace) / 2
    eod_times, _ = detect_eod_times(time, trace, threshold=threshold)

    # fix values equaling 0 in eod_times
    for idx, e in enumerate(eod_times):
        if e == 0:
            pre_interval = (eod_times[idx - 1] - eod_times[idx - 2])
            eod_times[idx] = eod_times[idx - 1] + pre_interval
    eod_times = eod_times[eod_times >= 0]
    # amplitude to frequency
    difference = np.diff(eod_times)
    frequency = 1 / difference
    return frequency, eod_times


def detect_eod_frequency_spectrum(time, eod, nfft=2**15, overlap=0.95, samplingrate=40000, segment_length=11.0,
                                  max_freq=1200):
    max_time = time[-1]
    segments = int(np.ceil(max_time / segment_length))

    for i in range(segments):
        start_time = i * segment_length
        segment = eod[(time >= start_time) & (time < start_time + segment_length)]
        print(len(segment))
        freqs, times, spectrogram = signal.spectrogram(segment, fs=samplingrate, nperseg=nfft, noverlap=overlap * nfft)
        spec = spectrogram[freqs < max_freq, :]
        freqs = freqs[freqs < max_freq]
        plt.imshow(spec, aspect='auto', origin='lower', interpolation='None')

        plt.show()

    exit()

    freqs, times, spectrogram = signal.spectrogram(eod, fs=samplingrate, nperseg=nfft, noverlap=overlap*nfft)
    frequencies = np.zeros_like(times)
    plt.imshow(spectrogram, aspect='auto', origin='lower')
    plt.ylim(0, 400)
    plt.show()
    for i in range(len(times)):
        psd = spectrogram[:, i]
        frequencies[i] = freqs[np.argmax(psd)]

    return times, frequencies


def jar_analysis(dataset, dataset_dict, keys):
    # load nix files, eod_array consists of amplitude values
    nf = nix.File.open(dataset, nix.FileMode.ReadOnly)

    b = nf.blocks[0]
    eod_array = b.data_arrays['EOD-1']
    dt = eod_array.dimensions[0].sampling_interval

    # for each key..
    for k in keys:
        print(k)
        # stripped key for file names
        k_str = str(k).replace(' ', '')

        loops_frequency = []
        loops_time = []
        loops_valid_eod = []
        loops_raw_eod = []
        loops_raw_time = []

        start = []
        stop = []
        timespan = []

        for mt_id, position in dataset_dict[k]:
            # retrieve eod trace
            mt = b.multi_tags[mt_id]
            # eod = mt.references("EOD-1")

            # retrieve pre_data (before stimulus onset to get reference)
            di = int(10.0/dt)
            i0 = int(mt.positions[position][0]/dt)
            i1 = i0 + int(mt.extents[position][0]/dt)
            pre_data = eod_array[i0-di:i0]

            # 'glue' eod and pre_data together
            trace = np.hstack((pre_data, eod_array[i0:i1]))
            trace = trace - np.mean(trace)

            # time for the length of whole data, including start/stop/timespan
            time = np.arange(0, len(trace), 1, dtype=np.double) * dt
            start.append(time[0])
            stop.append(time[-1])
            timespan.append((np.arange(0, len(trace)) * dt)[-1])

            'smoothing data by small filter'
            print('smoothing..')
            kernel_core = 5
            kernel = np.ones(kernel_core) / kernel_core

            # create head and tail filled with mean
            head_mean = np.mean(trace[:kernel_core])
            head = np.full((1, kernel_core), head_mean)
            head = head[0]

            tail_mean = np.mean(trace[kernel_core:])
            tail = np.full((1, kernel_core), tail_mean)
            tail = tail[0]

            # prolong trace with head and tail
            prolonged_trace = np.hstack((head, trace, tail))

            # use new freq with mode same, boundarys effects are outside of wanted time now
            prolonged_convolve_trace = np.convolve(kernel, prolonged_trace, mode='same')

            # remove head and tail and therefore boundaries
            prolonged_convolve_trace = prolonged_convolve_trace[kernel_core:]
            prolonged_convolve_trace = prolonged_convolve_trace[:-kernel_core]

            trace = prolonged_convolve_trace - np.mean(prolonged_convolve_trace)

            # duration (extents is only for eod data), onset und offset of stimulus
            offset = (np.arange(0, len(trace)) * dt)[-1]
            onset = (np.arange(0, len(pre_data) * dt))[-1]

            eod_times, _ = detect_eod_times(time, trace, threshold=np.mean(trace))

            # amplitude to frequency
            difference = np.diff(eod_times)
            for idx, d in enumerate(difference):
                # if difference == 0 than take value after
                if d == 0:
                    difference[idx] = difference[idx+1]

            frequency = 1 / difference

            # filtering data
            freq_filt = filter_data(frequency, n=1500)

            print('validating..')

            eodf = np.mean(frequency)
            period = 1 / eodf
            segment = 1.25 * period

            # sort out eod_times bigger than last eod_time or smaller than 0
            for idx, e in enumerate(eod_times):
                if e > eod_times[-1]:
                    eod_times[idx] = eod_times[idx + 1] - period
                # if e < eod_times[idx - 1]:
                #    eod_times[idx] = eod_times[idx - 1] + period
            eod_times = eod_times[eod_times >= 0]

            # make window for every eod_time, get max out of it
            eod_max = []
            for et in eod_times:
                start_segment = et - segment / 2
                stop_segment = et + segment / 2
                window_eod = trace[(time >= start_segment) & (time < stop_segment)]
                # as this has caused problems often..
                if len(window_eod) == 0:
                    print('window_eod empty')
                    embed()
                max_eod = np.max(window_eod)
                eod_max.append(max_eod)

            # valid eod = eod values bigger than the half of the maximum eod (to filter out fish turns)
            valid_eod = eod_max > (0.6 * np.median(eod_max))
            if len(valid_eod) > len(freq_filt):
                valid_eod = valid_eod[:len(freq_filt)]
            if len(valid_eod) < len(freq_filt):
                freq_filt = freq_filt[:len(valid_eod)]

            # valid eod contains either True (bigger than 0.5*max) or False (smaller than 0.5*max)
            # values smaller (False) will be but as NaN, next step in chirp_analysis2
            freq_filt[valid_eod < 1.0] = np.nan

            # append the whole data to lists
            loops_frequency.append(freq_filt)
            loops_time.append(eod_times[:-1])
            loops_valid_eod.append(valid_eod)
            loops_raw_eod.append(trace)
            loops_raw_time.append(time)

        # save data to npy files at the following places
        savepath = '/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/%s' % (dataset[-17:-4], k_str)
        key_savepath = '/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset[-17:-4]

        np.save(key_savepath + '/%s_key.npy' % k_str, k_str)
        np.save(savepath + '/%s_loops_frequency.npy' % k_str, loops_frequency)
        np.save(savepath + '/%s_loops_time.npy' % k_str, loops_time)
        np.save(savepath + '/%s_loops_raw_eod.npy' % k_str, loops_raw_eod)
        np.save(savepath + '/%s_loops_raw_time.npy' % k_str, loops_raw_time)
        np.save(savepath + '/%s_loops_valid_eod.npy' % k_str, loops_valid_eod)
        np.save(savepath + '/%s_stop.npy' % k_str, stop)
        np.save(savepath + '/%s_start.npy' % k_str, start)
        np.save(savepath + '/%s_timespan.npy' % k_str, timespan)

    pass


def chirp_analysis(dataset, dataset_dict, keys, id):
    # load nix files, eod_array consists of amplitude values
    nf = nix.File.open(dataset, nix.FileMode.ReadOnly)
    b = nf.blocks[0]
    eod_array = b.data_arrays['EOD-1']
    dt = eod_array.dimensions[0].sampling_interval

    for k in keys:
        print(k)
        # stripped key for file names
        k_str = str(k).replace(' ', '')

        loops_frequency = []
        loops_time = []
        loops_raw_eod = []
        loops_raw_time = []
        loops_valid_eod = []

        start = []
        stop = []
        timespan = []

        for mt_id, position in dataset_dict[k]:         # schau ma hier: weird mt_ids und positions
            # retrieve eod trace
            mt = b.multi_tags[mt_id]
            # eod = mt.references("EOD-1")

            # retrieve pre_data (before stimulus onset to get reference)
            di = int(10.0 / dt)
            i0 = int(mt.positions[position][0] / dt)
            i1 = i0 + int(mt.extents[position][0] / dt)
            pre_data = eod_array[i0 - di:i0]

            # 'glue' eod and pre_data together
            trace = np.hstack((pre_data, eod_array[i0:i1]))


            trace = trace - np.median(trace)

            # time for the length of whole data, including start/stop/timespan
            time = np.arange(0, len(trace), 1, dtype=np.double) * dt

            start.append(time[0])
            stop.append(time[-1])
            timespan.append((np.arange(0, len(trace)) * dt)[-1])

            'smoothing data by small filter'
            print('smoothing..')
            kernel_core = 5
            kernel = np.ones(kernel_core) / kernel_core

            # create head and tail filled with mean
            head_mean = np.mean(trace[:kernel_core])
            head = np.full((1, kernel_core), head_mean)
            head = head[0]

            tail_mean = np.mean(trace[kernel_core:])
            tail = np.full((1, kernel_core), tail_mean)
            tail = tail[0]

            # prolong trace with head and tail
            prolonged_trace = np.hstack((head, trace, tail))

            # use new freq with mode same, boundarys effects are outside of wanted time now
            prolonged_convolve_trace = np.convolve(kernel, prolonged_trace, mode='same')

            # remove head and tail and therefore boundaries
            prolonged_convolve_trace = prolonged_convolve_trace[kernel_core:]
            prolonged_convolve_trace = prolonged_convolve_trace[:-kernel_core]

            trace = prolonged_convolve_trace - np.mean(prolonged_convolve_trace)

            # duration (extents is only for eod data), onset und offset of stimulus
            offset = (np.arange(0, len(trace)) * dt)[-1]
            onset = (np.arange(0, len(pre_data) * dt))[-1]

            frequency, eod_times = detect_eod_frequency(time, trace)
            eodf = np.median(frequency)

            # times, frequency = detect_eod_frequency_spectrum(time, trace, nfft=2**15, overlap=0.999)

            print('validating..')
            period = 1 / eodf
            segment = 1.25 * period

            # filter eod_times bigger than the last eod_time
            for idx, e in enumerate(eod_times):
                if e > eod_times[-1]:
                    eod_times[idx] = eod_times[idx + 1] - period

            # make window for every eod_time, get max out of it
            eod_max = []
            for et in eod_times:
                start_segment = et - segment/2
                stop_segment = et + segment/2
                window_eod = trace[(time >= start_segment) & (time < stop_segment)]
                if len(window_eod) == 0:
                    print('window_eod empty')
                    embed()
                max_eod = np.max(window_eod)
                eod_max.append(max_eod)

            # valid eod = eod values bigger than the half of the maximum eod (to filter out fish turns)
            valid_eod = eod_max > (0.6 * np.max(eod_max))
            valid_eod = valid_eod[:-1]

            # valid eod contains either True (bigger than 0.5*max) or False (smaller than 0.5*max)
            # values smaller (False) will be but as NaN, next step in chirp_analysis2
            frequency[valid_eod < 1.0] = np.nan

            eod_times = eod_times[:-1]

            # append the whole data to lists
            loops_valid_eod.append(valid_eod)
            loops_time.append(eod_times)
            loops_frequency.append(frequency)
            loops_raw_eod.append(trace)
            loops_raw_time.append(time)

            # plt.plot(time, trace)
            # plt.scatter(eod_times, valid_eod, color='orange')
            # plt.show()

        # save data to npy files at the following places
        savepath = '/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/%s' % (dataset[-17:-4], k_str)
        key_savepath = '/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset[-17:-4]

        np.save(key_savepath + '/%s_key.npy' % k_str, k_str)
        np.save(savepath + '/%s_loops_frequency.npy' % k_str, loops_frequency)
        np.save(savepath + '/%s_loops_time.npy' % k_str, loops_time)
        np.save(savepath + '/%s_loops_raw_eod.npy' % k_str, loops_raw_eod)
        np.save(savepath + '/%s_loops_raw_time.npy' % k_str, loops_raw_time)
        np.save(savepath + '/%s_loops_valid_eod.npy' % k_str, loops_valid_eod)
        np.save(savepath + '/%s_stop.npy' % k_str, stop)
        np.save(savepath + '/%s_start.npy' % k_str, start)
        np.save(savepath + '/%s_timespan.npy' % k_str, timespan)

    pass


if __name__ == '__main__':
    t = np.arange(0, 40, 0.1)
    y = jar_fit_function2(t, 2.2, 10)
    plt.plot(t, y)
    plt.show()
    pass
