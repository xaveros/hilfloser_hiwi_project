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


def chirp_height_time(chirp_times, time, freq, big_small_chirp_threshold):
    small_chirps = []
    small_chirps_times = []
    big_chirps = []
    big_chirps_times = []
    for chirp in chirp_times:
        # window for each chirp and frequency in it
        start_segment = chirp - 0.1
        stop_segment = chirp + 0.1
        window_chirp = freq[(time >= start_segment) & (time < stop_segment)]
        if len(window_chirp) == 0:
            print('window empty')
            # embed()
        # height (=max) and height_time where max
        height = np.max(window_chirp)
        height_idx = np.where(freq == height)[0][0]
        height_time = time[height_idx]
        if height <= big_small_chirp_threshold:
            small_chirps.append(height)
            small_chirps_times.append(height_time)
        if height > big_small_chirp_threshold:
            big_chirps.append(height)
            big_chirps_times.append(height_time)
    return small_chirps, small_chirps_times, big_chirps, big_chirps_times


def main():
    datafolder = '/home/localadmin/data/electricbehaviour/recordings'
    datasets = data_finder(datafolder)
    chirp_keys = [(150.0, 750.0, False), (-150.0, 750.0, False), (150.0, 0.0, False), (-150.0, 0.0, False),
                  (50.0, 0.0, False), (-50.0, 0.0, False)]


    for dataset in datasets:
        dataset = dataset[-17:-4]
        if dataset == '2021-03-16-af':
            continue
        id = load_id(datafolder + '/' + dataset + '/' + dataset + '.nix')
        comment = load_comment(datafolder + '/' + dataset + '/' + dataset + '.nix')[0]

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

            chirps_numbers = []
            chirps_big_numbers = []
            chirps_small_height = []
            chirps_big_height = []
            for idx, freq in enumerate(loops_frequency):
                print('loop number:', idx)

                eod = loops_raw_eod[idx]
                eod_times = loops_eod_time[idx]
                valid_eod = loops_valid_eod[idx]
                time = loops_raw_time[idx]

                # correction of false eod_times values (values of 6s or something at 0.01s time), put in analysis
                eodf = np.nanmean(freq)
                period = 1 / eodf
                for idx1, e in enumerate(eod_times):
                    if e > 5 * np.mean(eod_times[idx1:idx1+10]):
                        eod_times[idx1] = eod_times[idx1 + 1] - period
                        print('eod_time corrected')
                valid_time = eod_times[valid_eod == 1]
                valid_true_freq = freq[valid_eod == 1]
                valid_freq = valid_true_freq - np.mean(valid_true_freq)

                # smoothing filter over frequency
                valid_freq = filter_data(valid_freq, n=3)

                # correct outliers
                for idx2, vf in enumerate(valid_freq[:25]):
                    if vf < -200:
                        valid_freq[idx2] = np.median(valid_freq[:50])
                        print('outlier corrected')
                # df if fakefish of 750 Hz was on
                if key[1] > 0:
                    fakefish_freq = key[1]
                    mean_freq = np.mean(valid_true_freq)
                    df = mean_freq - fakefish_freq

                'chirp detection'
                chirp_threshold = 30

                chirp_times = threshold_crossing(valid_freq, valid_time, chirp_threshold)

                chirp_number = len(chirp_times)

                'chirp height and precise chirp time'
                # frequency threshold for distinction of big and small chirp (300 Hz good?)
                big_small_chirp_threshold = 300
                # for chirps in positive direction, for big and small chirps

                small_chirps, small_chirps_times, big_chirps, big_chirps_times = \
                    chirp_height_time(chirp_times, valid_time, valid_freq, big_small_chirp_threshold)

                # if chirp_number > 0:
                print('chirp number:', chirp_number)
                print('chirp times:', chirp_times)

                chirps_numbers.append(chirp_number)
                chirps_big_numbers.append(len(big_chirps))
                chirps_big_height.append(big_chirps)
                chirps_small_height.append(small_chirps)

                # fig, ax = plt.subplots(figsize=(11.6, 8.2))
                # # plot raw data
                # ax.plot(time, eod, color='C0')
                # ax.set_ylabel('amplitude [mV]', color='C0')
                #
                # ax2 = ax.twinx()
                # # plot frequency
                # ax2.plot(valid_time, valid_freq, color='orange')
                # # scatter chirps
                # ax2.scatter(small_chirps_times, small_chirps, color='red', lw=3, zorder=3)
                # ax2.scatter(big_chirps_times, big_chirps, color='yellow', lw=3, zorder=3)
                # ax2.set_ylabel('frequency [Hz]', color='orange')
                #
                # # threshold lines
                # plt.axhline(chirp_threshold, 0, 40, lw=2, color='black')
                #
                # plt.xlabel('time [s]')
                # if key[1] > 0:
                #     plt.title('%s, %s, %s, delta F: %s' % (id, comment, key, df))
                # else:
                #     plt.title('%s, %s, %s' % (id, comment, key))
                # plt.show()
                #
                # plt.savefig('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/chirp_plots/%s/'
                #             '%s, %s, %s, loop_%s.png' % (dataset, k_str, id, comment, key, idx))
                # plt.close()
                #

            data = [id, comment, k_str, round(np.mean(chirps_numbers), 2), round(np.std(chirps_numbers), 2),
                    round(np.mean(chirps_big_numbers), 2), round(np.std(chirps_big_numbers), 2)]

            print('-------------------------------------')

            os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)
            savepath = '/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/%s' % (dataset[-17:], k_str)

            np.save(savepath + '/%s_data.npy' % k_str, data)
            print(data)
    embed()
    quit()

if __name__ == '__main__':
    main()