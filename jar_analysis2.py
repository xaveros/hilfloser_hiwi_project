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

os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves')
chirp_keys = [(150.0, 750.0, False), (-150.0, 0.0, False), (150.0, 0.0, False), (50.0, 0.0, False), (-150.0, 750.0, False),
               (-50.0, 0.0, False)]

for key in chirp_keys:
    print('key:', key)

    # loads
    k_str = str(key).replace(' ', '')
    load_key = np.load('%s_key.npy' % k_str)
    stop = np.load('%s_stop.npy' % load_key)
    start = np.load('%s_start.npy' % load_key)
    timespan = np.load('%s_timespan.npy' % load_key)
    loops_frequency = np.load('%s_loops_frequency.npy' % load_key, allow_pickle=True)
    loops_time = np.load('%s_loops_time.npy' % load_key, allow_pickle=True)
    loops_eod = np.load('%s_loops_eod.npy' % load_key, allow_pickle=True)
    loops_valid_eod = np.load('%s_loops_valid_eod.npy' % load_key, allow_pickle=True)


    # loops frequency set to True or False. Values who were smaller than 0.5*max are NaN, by ~ set to False
    # the rest (who is not NaN) is set to True, giving us a matrix with 0's (False) and 1's (True)
    loops_frequency_T = []

    for l in loops_frequency:
        l_T = ~np.isnan(l)
        loops_frequency_T.append(l_T)

    # mean over all loops
    freq_matrix, tnew_freq = mean_traces_data(loops_frequency_T, loops_time, np.mean(start), np.mean(stop), np.mean(timespan))

    # same done for valid_eod with True (1) and False (0) in it
    eod_matrix, tnew_eod = mean_traces_data(loops_valid_eod, loops_time, np.mean(start), np.mean(stop), np.mean(timespan))

    mean_matrix = eod_matrix / freq_matrix

    # new list with time and frequency fulfilling the condition of valid_eod
    ttt = []
    fff = []
    for idx, freq in enumerate(loops_frequency):
        print('loop number:', idx)

        eod = loops_eod[idx]
        valid_eod = loops_valid_eod[idx]

        # temporal time
        dt = 2.5 * 10**-5
        time = np.arange(0, len(eod), 1, dtype=np.double) * dt
        tt = loops_time[idx][loops_valid_eod[idx]]

        ff = freq[valid_eod == 1]
        ttt.append(tt)
        fff.append(ff)
        freq_filt = filter_data(ff, n=500)
        kernel_core = 10
        kernel = np.ones(kernel_core) / kernel_core
        convolve_freq = np.convolve(kernel, ff, mode='same')

        convolve_freq = convolve_freq[kernel_core + kernel_core * 2:]  # schau ma hier: Anfänge abkappen
        tt = tt[kernel_core + kernel_core * 2:]

        threshold_value = 50
        threshold = threshold_value
        threshold2 = -threshold_value
        chirp_times = threshold_crossing(convolve_freq, tt, threshold)
        chirp_times2 = threshold_crossing(convolve_freq, tt, threshold2)

        chirp_number = len(chirp_times) + len(chirp_times2)
        if chirp_number > 0:
            print('chirp number:', chirp_number)
            print('chirp times upper threshold:', chirp_times)
            print('chirp times lower threshold:', chirp_times2)

            fig, ax = plt.subplots()
            ax.plot(time, eod, color='C0')
            ax.set_ylabel('amplitude [mV]', color='C0')


            ax2 = ax.twinx()
            #ax2.plot(tt, convolve_freq, color='orange')
            ax2.scatter(loops_time[idx][valid_eod], ff, color='orange')
            ax2.set_ylabel('frequency [Hz]', color='orange')

            # plt.xlim([0, 40])
            # plt.ylim([-60, 60])
            # plt.axhline(threshold, 0, 40, lw=2, color='black')
            # plt.axhline(threshold2, 0, 40, lw=2, color='black')
            plt.show()
    print('-------------------------------------')
embed()
quit()