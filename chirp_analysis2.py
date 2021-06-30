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
from main import load_id
from main import load_comment

datafolder = '/home/localadmin/data/electricbehaviour/recordings'
datasets = data_finder(datafolder)
chirp_keys = [(150.0, 750.0, False), (-150.0, 750.0, False), (150.0, 0.0, False), (-150.0, 0.0, False),
              (50.0, 0.0, False), (-50.0, 0.0, False)]

for dataset in datasets:
    dataset = dataset[-17:-4]
    if dataset == '2021-03-15-ab':  # temporaly because data is loaded there
        id = load_id(datafolder + '/' + dataset + '/' + dataset + '.nix')
        comment = load_comment(datafolder + '/' + dataset + '/' + dataset + '.nix')

        os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

        for key in chirp_keys:
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

                # correction of false eod_times values (values of 6s or something at 0.01s time), put in analysis
                eodf = np.nanmean(freq)
                period = 1 / eodf
                for idx, e in enumerate(eod_times):
                    if e > 5 * np.mean(eod_times[idx:idx+10]):
                        eod_times[idx] = eod_times[idx + 1] - period

                valid_time = eod_times[valid_eod == 1]
                valid_true_freq = freq[valid_eod == 1]
                valid_freq = valid_true_freq - np.mean(valid_true_freq)

                valid_freq = filter_data(valid_freq, n=3)

                for idx, vf in enumerate(valid_freq[:25]):
                    if vf < -200:
                        valid_freq[idx] = np.median(valid_freq[:50])

                if key[1] > 0:
                    fakefish_freq = key[1]
                    mean_freq = np.mean(valid_true_freq)
                    df = mean_freq - fakefish_freq

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

                # for chirps in positive direction
                small_chirps1 = []
                small_chirps_times1 = []
                big_chirps1 = []
                big_chirps_times1 = []
                for chirp in chirp_times1:
                    start_segment = chirp - 0.1
                    stop_segment = chirp + 0.1
                    window_chirp = valid_freq[(valid_time >= start_segment) & (valid_time < stop_segment)]
                    if len(window_chirp) == 0:
                        embed()
                    height = np.max(window_chirp)
                    height_idx = np.where(valid_freq == height)[0][0]
                    height_time = valid_time[height_idx]
                    if height < 200:
                        small_chirps1.append(height)
                        small_chirps_times1.append(height_time)
                    if height > 350:
                        big_chirps1.append(height)
                        big_chirps_times1.append(height_time)
                # for chirps in negative direction
                small_chirps2 = []
                small_chirps_times2 = []
                big_chirps2 = []
                big_chirps_times2 = []
                for chirp in chirp_times2:
                    start_segment = chirp - 0.1
                    stop_segment = chirp + 0.1
                    window_chirp = valid_freq[(valid_time >= start_segment) & (valid_time < stop_segment)]
                    if len(window_chirp) == 0:
                        embed()
                    height = np.min(window_chirp)
                    height_idx = np.where(valid_freq == height)[0][0]
                    height_time = valid_time[height_idx]
                    if height > -200:
                        small_chirps2.append(height)
                        small_chirps_times2.append(height_time)
                    if height < -350:
                        big_chirps2.append(height)
                        big_chirps_times2.append(height_time)


                # if chirp_number > 0:
                print('chirp number:', chirp_number)
                print('chirp times upper threshold:', chirp_times1)
                print('chirp times lower threshold:', chirp_times2)

                fig, ax = plt.subplots()
                ax.plot(time, eod, color='C0')
                ax.set_ylabel('amplitude [mV]', color='C0')

                ax2 = ax.twinx()
                #ax2.plot(tt, convolve_freq, color='orange')
                ax2.plot(valid_time, valid_freq, color='orange')
                ax2.scatter(small_chirps_times1, small_chirps1, color='red', lw=3, zorder=3)
                ax2.scatter(small_chirps_times2, small_chirps2, color='red', lw=3, zorder=3)
                ax2.scatter(big_chirps_times1, big_chirps1, color='yellow', lw=3, zorder=3)
                ax2.scatter(big_chirps_times2, big_chirps2, color='yellow', lw=3, zorder=3)
                ax2.set_ylabel('frequency [Hz]', color='orange')

                plt.axhline(threshold, 0, 40, lw=2, color='black')
                plt.axhline(threshold2, 0, 40, lw=2, color='black')
                plt.xlabel('time [s]')
                if key[1] > 0:
                    plt.title('%s, %s, %s, delta F: %s' % (id, comment, key, df))
                else:
                    plt.title('%s, %s, %s' % (id, comment, key))
                # plt.show()

                plt.savefig('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/chirp_plots/'
                            '%s, %s, %s, loop_%s.png' % (dataset, id, comment, key, idx))
                # embed()
            print('-------------------------------------')

            os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

        embed()
        quit()