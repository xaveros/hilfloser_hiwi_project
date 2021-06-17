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
from analysis import mean_traces_data
from analysis import filter_data
from analysis import threshold_crossing
from analysis import filter_data
from main import data_finder

datafolder = '/home/localadmin/data/electricbehaviour/recordings'
datasets = data_finder(datafolder)
echo_keys = [(-50.0, 0.0, True), (50.0, 0.0, True)]

for dataset in datasets:
    dataset = dataset[-17:-4]
    if dataset == '2021-03-15-aa':  # temporaly because data is loaded there

        os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

        for key in echo_keys:
            print(dataset)
            print('key:', key)
            k_str = str(key).replace(' ', '')

            load_key = np.load('%s_key.npy' % k_str)

            os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/%s' % (dataset, load_key))

            # loads
            stop = np.load('%s_stop.npy' % load_key)
            start = np.load('%s_start.npy' % load_key)
            timespan = np.load('%s_timespan.npy' % load_key)
            loops_frequency = np.load('%s_loops_frequency.npy' % load_key, allow_pickle=True)
            loops_eod_time = np.load('%s_loops_time.npy' % load_key, allow_pickle=True)
            loops_raw_time = np.load('%s_loops_raw_time.npy' % load_key, allow_pickle=True)
            loops_raw_eod = np.load('%s_loops_raw_eod.npy' % load_key, allow_pickle=True)
            loops_valid_eod = np.load('%s_loops_valid_eod.npy' % load_key, allow_pickle=True)

            for idx, freq in enumerate(loops_frequency):
                print('loop number:', idx)

                eod = loops_raw_eod[idx]
                eod_times = loops_eod_time[idx]
                valid_eod = loops_valid_eod[idx]
                time = loops_raw_time[idx]
                art_chirps = np.arange(1, 59, 1)

                # correction of false eod_times values (values of 6s or something at 0.01s time), put in analysis
                eodf = np.nanmean(freq)
                period = 1 / eodf
                for idx, e in enumerate(eod_times):
                    if e > 5 * np.mean(eod_times[idx:idx+10]):
                        eod_times[idx] = eod_times[idx + 1] - period

                valid_time = eod_times[valid_eod == 1]
                valid_freq = freq[valid_eod == 1]
                valid_freq = valid_freq - np.mean(valid_freq)

                valid_freq = filter_data(valid_freq, n=3)

                for idx, vf in enumerate(valid_freq[:25]):
                    if vf < -200:
                        valid_freq[idx] = np.median(valid_freq[:50])

                threshold_value = 30
                threshold = threshold_value
                threshold2 = -threshold_value

                chirp_times1 = threshold_crossing(valid_freq, valid_time, threshold)
                chirp_times2 = threshold_crossing(valid_freq, valid_time, threshold2)

                chirp_times1 = chirp_times1.tolist()
                chirp_times2 = chirp_times2.tolist()
                chirp_times = chirp_times1 + chirp_times2

                chirp_times = sorted(chirp_times)
                chirp_number = len(chirp_times)

                chirp_height = []
                for chirp in chirp_times:
                    start_segment = chirp - 0.1
                    stop_segment = chirp + 0.1
                    window_chirp = valid_freq[(valid_time >= start_segment) & (valid_time < stop_segment)]
                    if len(window_chirp) == 0:
                        embed()
                    height = np.max(window_chirp)
                    chirp_height.append(height)


                'align art_chirps to chirps'
                echo_time = []
                for c in chirp_times:
                    c_floor = np.floor(c)
                    echo = c - c_floor
                    echo_time.append(echo)
                # embed()


                if chirp_number > 0:
                    fig, ax = plt.subplots()
                    ax.plot(time, eod, color='C0')
                    ax.set_ylabel('amplitude [mV]', color='C0')

                    ax2 = ax.twinx()
                    #ax2.plot(tt, convolve_freq, color='orange')
                    ax2.plot(valid_time, valid_freq, color='orange')
                    ax2.scatter(art_chirps, np.full_like(art_chirps, 10), color='red', lw=3, zorder=3)
                    ax2.scatter(chirp_times, np.full_like(chirp_times, 10), color='green', lw=3, zorder=3)
                    ax2.set_ylabel('frequency [Hz]', color='orange')

                    plt.axhline(threshold, 0, 40, lw=2, color='black')
                    plt.axhline(threshold2, 0, 40, lw=2, color='black')
                    plt.show()

                    plt.scatter(echo_time, chirp_height)
                    plt.show()
                    embed()
            print('-------------------------------------')

            os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

        embed()
        quit()