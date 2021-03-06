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
from chirp_analysis2 import chirp_height_time

def gauss_kernel(sigma, dt):
    x = np.arange(-4*sigma, 4*sigma, dt)
    y = np.exp(-0.5 * (x/sigma)**2) / (np.sqrt(2 * np.pi)/sigma)
    return x, y


def echo_time_difference(chirp_times):
    echo_times = []
    for c in chirp_times:
        if len(chirp_times) == 0:
            continue
        # c_floor as reference: round down to last integer before (as chirps has been on every full second)
        c_floor = np.floor(c)
        echo = c - c_floor
        echo_times.append(echo)
    return echo_times

def echo_response(echo_chirps_times):
    dt = 1. / 40000
    echo_time = np.arange(.0, 1.0, dt)
    _, kernel = gauss_kernel(0.05, dt)
    response = np.zeros_like(echo_time)
    for ect in echo_chirps_times:
        response[int(ect // dt)] += 1
    response = np.convolve(response, kernel, mode="same")
    return response, echo_time


def main():
    datafolder = '/home/localadmin/data/electricbehaviour/data_extension'
    datasets = data_finder(datafolder)
    echo_keys = [(50.0, 0.0, True), (-50.0, 0.0, True)]

    for dataset in datasets:
        dataset = dataset[-17:-4]
        if dataset == '2021-03-16-ae':
            continue

        id = load_id(datafolder + '/' + dataset + '/' + dataset + '.nix')
        comment = load_comment(datafolder + '/' + dataset + '/' + dataset + '.nix')[0]

        os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

        for key in echo_keys:
            if dataset == '2021-08-24-ab':
                if key == (-50.0, 0.0, True):
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

                    echo_chirps_times = []
                    chirps_numbers = []
                    chirps_big_numbers = []

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
                        valid_freq = valid_freq - np.median(valid_freq)
                        embed()
                        # smoothing filter over frequency
                        valid_freq = filter_data(valid_freq, n=3)

                        # correct outliers
                        for idx2, vf in enumerate(valid_freq[:25]):
                            if vf < -200:
                                valid_freq[idx2] = np.median(valid_freq[:50])
                                print('outliers corrected')
                        outliers = []
                        for idx3, f in enumerate(valid_freq):
                            if f > 1000 or f < -1000:
                                valid_freq[idx3] = np.median(valid_freq[idx3-50:idx3])
                                print('outliers corrected')
                                outliers.append(f)
                        # if len(outliers) > 10:
                        #     embed()
                        #     quit()
                        'chirp detection'
                        chirp_threshold = 30

                        chirps_times = threshold_crossing(valid_freq, valid_time, chirp_threshold)

                        chirps_number = len(chirps_times)

                        'chirp height and precise chirp time'
                        # frequency threshold for distinction of big and small chirp (300 Hz good?)
                        big_small_chirp_threshold = 300
                        # for chirps in positive direction, for big and small chirps
                        small_chirps, small_chirps_times, big_chirps, big_chirps_times = \
                            chirp_height_time(chirps_times, valid_time, valid_freq, big_small_chirp_threshold)

                        chirps_numbers.append(chirps_number)
                        chirps_big_numbers.append(len(big_chirps))

                        # if chirp_number > 0:
                        print('chirp number:', chirps_number)
                        print('chirp times:', chirps_times)

                        'time difference to artifical chirp before'
                        # !!! note that artificial chirps have been assumed at every full second !!!
                        echo_small_chirps_times = echo_time_difference(small_chirps_times)
                        echo_big_chirps_times = echo_time_difference(big_chirps_times)

                        for esc in echo_small_chirps_times:
                            echo_chirps_times.append(esc)
                        for ebc in echo_big_chirps_times:
                            echo_chirps_times.append(ebc)

                        # # plots
                        # # #if chirp_number > 0:
                        # fig, ax = plt.subplots(figsize=(11.6, 8.2))
                        # # plot raw data
                        # ax.plot(time, eod, color='C0')
                        # ax.set_ylabel('amplitude [mV]', color='C0')
                        #
                        # ax2 = ax.twinx()
                        # # plot frequency
                        # ax2.plot(valid_time, valid_freq, color='orange')
                        #
                        # # plot articifical chirps
                        # ax2.scatter(art_chirps, np.full_like(art_chirps, 10), color='green', lw=3, zorder=3)
                        #
                        # # plot detected chirps
                        # ax2.scatter(small_chirps_times, small_chirps, color='red', lw=3, zorder=3)
                        # ax2.scatter(big_chirps_times, big_chirps, color='yellow', lw=3, zorder=3)
                        # ax2.set_ylabel('frequency [Hz]', color='orange')
                        #
                        # # plot threshold
                        # plt.axhline(chirp_threshold, 0, 40, lw=2, color='black')
                        # plt.show()

                        # plt.savefig('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/echo_plots/%s/'
                        #            '%s, %s, %s, loop_%s.png' % (dataset, k_str, id, comment, key, idx))

            'chirp frequency (or chirp rate) over all loops, frequency computed for window_size'

    #         dt = 1. / 40000
    #         echo_time = np.arange(0, 1, dt)
    #         _, kernel = gauss_kernel(0.05, dt)
    #         response_all = np.zeros_like(echo_time)
    #         for ect in echo_chirps_times:
    #             response_all[int(ect // dt)] += 1
    #         response_all = np.convolve(response_all, kernel, mode="same")
    #
    #         response, echo_time = echo_response(echo_chirps_times)
    #
    #         max_response = np.max(response)
    #         min_response = np.min(response)
    #         mean_response = np.mean(response)
    #
    #         diff_response = max_response - min_response
    #
    #         response_ratio = diff_response / mean_response
    #         if len(echo_chirps_times) == 0:
    #             response_ratio = 0
    #
    #         # plt.plot(echo_time, response_all)
    #         # plt.plot([echo_time[0], echo_time[-1]], [mean_response, mean_response], ls='--', color='gray',
    #         #          label='mean')
    #         # plt.xlabel('response time to artifical chirp [s]')
    #         # plt.ylabel('chirp frequency [Hz]')
    #         # plt.legend(title='response ratio: %s' % response_ratio)
    #         # plt.title('%s, %s, %s' % (id, comment, key))
    #         #
    #         # plt.show()
    #
    #         # plt.savefig('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/echo_plots/%s/'
    #         #            'chirp_frequency: %s, %s, %s.png' % (dataset, k_str, id, comment, key))
    #         # plt.close()
    #
    #         print('-------------------------------------')
    #
    #         data = [id, comment, k_str, round(np.mean(chirps_numbers), 2), round(np.std(chirps_numbers), 2),
    #                 round(np.mean(chirps_big_numbers), 2), round(np.std(chirps_big_numbers), 2),
    #                 round(response_ratio, 2)]
    #
    #         os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)
    #
    #         savepath = '/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/%s' % (dataset[-17:], k_str)
    #
    #         np.save(savepath + '/%s_data.npy' % k_str, data)
    # embed()
    # quit()


if __name__ == '__main__':
    main()
