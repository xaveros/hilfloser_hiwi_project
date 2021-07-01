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

def gauss_kernel(sigma, dt):
    x = np.arange(-4*sigma, 4*sigma, dt)
    y = np.exp(-0.5 * (x/sigma)**2) / (np.sqrt(2 * np.pi)/sigma)
    return x, y


datafolder = '/home/localadmin/data/electricbehaviour/recordings'
datasets = data_finder(datafolder)
echo_keys = [(50.0, 0.0, True), (-50.0, 0.0, True)]

for dataset in datasets:
    dataset = dataset[-17:-4]
    if dataset == '2021-03-15-ab':  # temporaly because data is loaded there
        id = load_id(datafolder + '/' + dataset + '/' + dataset + '.nix')
        comment = load_comment(datafolder + '/' + dataset + '/' + dataset + '.nix')

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

            echo_chirp_times = []

            for idx, freq in enumerate(loops_frequency):
                print('loop number:', idx)

                eod = loops_raw_eod[idx]
                eod_times = loops_eod_time[idx]
                valid_eod = loops_valid_eod[idx]
                time = loops_raw_time[idx]

                start_art_chirps = 1
                stop_art_chirps = 59
                art_chirps = np.arange(1, 59, 1)

                # correction of false eod_times values (values of 6s or something at 0.01s time), put in analysis
                eodf = np.nanmean(freq)
                period = 1 / eodf
                for idx1, e in enumerate(eod_times):
                    if e > 5 * np.mean(eod_times[idx1:idx1+10]):
                        eod_times[idx1] = eod_times[idx1 + 1] - period

                valid_time = eod_times[valid_eod == 1]
                valid_freq = freq[valid_eod == 1]
                valid_freq = valid_freq - np.mean(valid_freq)

                # smoothing filter over frequency
                valid_freq = filter_data(valid_freq, n=3)

                # correct outliers
                for idx2, vf in enumerate(valid_freq[:25]):
                    if vf < -200:
                        valid_freq[idx2] = np.median(valid_freq[:50])
                for idx3, f in enumerate(valid_freq):
                    if f > 1000 or f < -1000:
                        valid_freq[idx3] = np.median(valid_freq[idx3-50:idx3])

                'chirp detection'
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

                'chirp height and precise chirp time'
                # frequency threshold for distinction of big and small chirp (300 Hz good?)
                big_small_chirp_threshold = 300
                # for chirps in positive direction, for big and small chirps
                small_chirps1 = []
                small_chirps_times1 = []
                big_chirps1 = []
                big_chirps_times1 = []
                for chirp in chirp_times1:
                    if chirp >= stop_art_chirps:
                        continue
                    start_segment = chirp - 0.1
                    stop_segment = chirp + 0.1
                    window_chirp = valid_freq[(valid_time >= start_segment) & (valid_time < stop_segment)]
                    if len(window_chirp) == 0:
                        embed()
                    height = np.max(window_chirp)
                    height_idx = np.where(valid_freq == height)[0][0]
                    height_time = valid_time[height_idx]
                    if height <= big_small_chirp_threshold:
                        small_chirps1.append(height)
                        small_chirps_times1.append(height_time)
                    if height > big_small_chirp_threshold:
                        big_chirps1.append(height)
                        big_chirps_times1.append(height_time)
                # for chirps in negative direction, for big and small chirps
                small_chirps2 = []
                small_chirps_times2 = []
                big_chirps2 = []
                big_chirps_times2 = []
                for chirp in chirp_times2:
                    if chirp >= stop_art_chirps:
                        continue
                    start_segment = chirp - 0.1
                    stop_segment = chirp + 0.1
                    window_chirp = valid_freq[(valid_time >= start_segment) & (valid_time < stop_segment)]
                    if len(window_chirp) == 0:
                        embed()
                    height = np.min(window_chirp)
                    height_idx = np.where(valid_freq == height)[0][0]
                    height_time = valid_time[height_idx]
                    if height > -big_small_chirp_threshold:
                        small_chirps2.append(height)
                        small_chirps_times2.append(height_time)
                    if height < -big_small_chirp_threshold:
                        big_chirps2.append(height)
                        big_chirps_times2.append(height_time)

                'time difference to artifical chirp before'
                # for positive/negative small/big chirps
                # !!! note that artificial chirps have been assumed at every full second !!!
                echo_small_chirps_time1 = []
                for c in small_chirps_times1:
                    # c_floor as reference: round down to last integer before (as chirps has been on every full second)
                    c_floor = np.floor(c)
                    echo = c - c_floor
                    echo_small_chirps_time1.append(echo)
                    echo_chirp_times.append(echo)
                echo_small_chirps_time2 = []
                for c in small_chirps_times2:
                    c_floor = np.floor(c)
                    echo = c - c_floor
                    echo_small_chirps_time2.append(echo)
                    echo_chirp_times.append(echo)
                echo_big_chirps_time1 = []
                for c in big_chirps_times1:
                    c_floor = np.floor(c)
                    echo = c - c_floor
                    echo_big_chirps_time1.append(echo)
                    echo_chirp_times.append(echo)
                echo_big_chirps_time2 = []
                for c in big_chirps_times2:
                    c_floor = np.floor(c)
                    echo = c - c_floor
                    echo_big_chirps_time2.append(echo)
                    echo_chirp_times.append(echo)

                'actual chirpfrequency per 50ms, not needed I guess'
                '''chirp_freq = []
                chirp_freq_times = []
                for idx, ac in enumerate(art_chirps):
                    art_chirps_freq = art_chirps[-1] / len(art_chirps)
                    start_intervall = ac
                    stop_intervall = ac + 1/art_chirps_freq
                    intervall_time = valid_time[(valid_time >= start_intervall) & (valid_time < stop_intervall)]

                    window_size = 0.05
                    window_intervall = np.arange(start_intervall, stop_intervall, window_size)
                    for i, wi in enumerate(window_intervall):
                        chirp_freq_times.append(wi)
                        window_time = intervall_time[(intervall_time > wi) & (intervall_time <= (wi + window_size))]
                        chirp_number_window = 0
                        for ct in chirp_times:
                            if ct < window_time[-1] and ct >= window_time[0]:
                                chirp_number_window += 1
                        if chirp_number_window == 0:
                            chirp_freq.append(0)
                        else:
                            chirp_freq_intervall = window_size / chirp_number_window
                            chirp_freq.append(chirp_freq_intervall)
                '''
                dt = 1./40000
                echo_time = np.arange(.0, 1.0, dt)
                _, kernel = gauss_kernel(0.05, dt)
                response = np.zeros_like(echo_time)
                for ct in small_chirps_times1:
                    ctt = np.floor(ct)
                    response_time = ct - ctt
                    response[int(response_time//dt)] += 1
                for ct in big_chirps_times1:
                    ctt = np.floor(ct)
                    response_time = ct - ctt
                    response[int(response_time//dt)] += 1
                response = np.convolve(response, kernel, mode="same")
                plt.plot(echo_time, response)
                plt.plot([echo_time[0], echo_time[-1]], [np.mean(response), np.mean(response)], ls='--', color='gray')
                plt.show()
                #quit()

                #if chirp_number > 0:
                fig, ax = plt.subplots(figsize=(11.6, 8.2))
                # plot raw data
                ax.plot(time, eod, color='C0')
                ax.set_ylabel('amplitude [mV]', color='C0')

                ax2 = ax.twinx()
                # plot frequency
                ax2.plot(valid_time, valid_freq, color='orange')

                # plot articifical chirps
                ax2.scatter(art_chirps, np.full_like(art_chirps, 10), color='green', lw=3, zorder=3)

                # plot detected chirps
                ax2.scatter(small_chirps_times1, small_chirps1, color='red', lw=3, zorder=3)
                ax2.scatter(small_chirps_times2, small_chirps2, color='red', lw=3, zorder=3)
                ax2.scatter(big_chirps_times1, big_chirps1, color='yellow', lw=3, zorder=3)
                ax2.scatter(big_chirps_times2, big_chirps2, color='yellow', lw=3, zorder=3)
                ax2.set_ylabel('frequency [Hz]', color='orange')

                # plot thresholds
                plt.axhline(threshold, 0, 40, lw=2, color='black')
                plt.axhline(threshold2, 0, 40, lw=2, color='black')
                #plt.savefig('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/echo_plots/%s/'
                #            '%s, %s, %s, loop_%s.png' % (dataset, k_str, id, comment, key, idx))
                # plt.show()
                plt.close()

                plt.scatter(echo_small_chirps_time1, small_chirps1, c='r')
                plt.scatter(echo_small_chirps_time2, small_chirps2, c='darkred')
                plt.scatter(echo_big_chirps_time1, big_chirps1, c='y')
                plt.scatter(echo_big_chirps_time2, big_chirps2, c='gold')
                plt.xlabel('time difference to artifical chirp [s]')
                plt.ylabel('chirp size [Hz]')
                plt.show()
                plt.close()

            'chirp frequency (or chirp rate) over all loops, frequency computed for window_size'
            # windows for which frequency gets detected, put in bins
            window_size = 0.05
            bin_widths = np.arange(0, 1, window_size)

            chirp_frequency = []
            for bw in bin_widths:
                # check if chirps lie within the window, if so marked with True
                # echo_chirp_times contain the chirps of all loops for this key
                number_echos = (echo_chirp_times >= bw) & (echo_chirp_times < (bw + window_size))
                # count the amount of True as number of chirps in this window
                number = 0
                for n in number_echos:
                    if n == True:
                        number += 1
                # chirp frequency: deviding the window_size by the number of chirps in it
                if number == 0:
                    chirp_frequency.append(0)
                else:
                    chirp_frequency.append(window_size / number)

            # print(echo_chirp_times)

            # plot frequency per bin
            plt.plot(bin_widths, chirp_frequency)
            plt.xlabel('response time to artifical chirp [s]')
            plt.ylabel('chirp frequency [Hz]')
            plt.title('')

            #plt.savefig('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/echo_plots/%s/'
            #            'chirp_frequency: %s, %s, %s.png' % (dataset, k_str, id, comment, key))
            plt.show()
            plt.close()

            print('-------------------------------------')

            os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

        embed()
        quit()