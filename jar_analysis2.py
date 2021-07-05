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
from analysis import jar_fit_function
from analysis import jar_fit_function2
from main import data_finder
from main import load_id
from main import load_comment

datafolder = '/home/localadmin/data/electricbehaviour/recordings'
datasets = data_finder(datafolder)
jar_keys = [(5.0, 0.0, False), (-5.0, 0.0, False)]

for dataset in datasets:
    dataset = dataset[-17:-4]

    if dataset == '2021-03-15-aa':  # temporaly because data is loaded there
        id = load_id(datafolder + '/' + dataset + '/' + dataset + '.nix')
        comment = load_comment(datafolder + '/' + dataset + '/' + dataset + '.nix')

        os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

        for key in jar_keys:
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

            # new list with time and frequency fulfilling the condition of valid_eod
            taus = []
            responses = []

            for idx, freq in enumerate(loops_frequency):
                # sort out bad recordings
                if dataset == '2021-03-15-ac':
                    if key == (5.0, 0.0, False):
                        if idx == 1 or idx == 2 or idx == 3 or idx == 4:
                            print('out')
                            continue
                    if key == (-5.0, 0.0, False):
                        if idx == 3:
                            print('out')
                            continue

                print('loop number:', idx)

                eod = loops_raw_eod[idx]
                time = loops_raw_time[idx]
                eod_times = loops_eod_time[idx]
                valid_eod = loops_valid_eod[idx]

                # fit for single loop
                valid_time = eod_times[valid_eod == 1]
                valid_freq = freq[valid_eod == 1]

                # absolute JAR response of base to after stimulus in Hz
                before_jar = np.mean(valid_freq[valid_time < 5])
                after_jar = np.mean(valid_freq[(valid_time < valid_time[-1]) & (valid_time > 35)])
                response = after_jar - before_jar
                responses.append(response)
                print('response in Hz:', response)

                valid_freq = valid_freq - before_jar

                # fit of frequency course
                # sv, sc = curve_fit(jar_fit_function, valid_time[valid_time > 10] - 10.0, valid_freq[valid_time > 10],
                #                    [2, 1, 20, 25])  # working: [2, 2, 10, 45]
                sv2, sc2 = curve_fit(jar_fit_function2, valid_time[valid_time > 10] - 10.0, valid_freq[valid_time > 10],
                                     [2, 5])  # working: [2, 2, 10, 45]

                # print('jar tau1:', sv[2])
                print('jar2 tau1:', sv2[1])
                taus.append(sv2[1])

                fig, ax = plt.subplots(figsize=(11.6, 8.2))
                # plot raw data
                # ax.plot(time, eod, color='C0')
                ax.set_ylabel('amplitude [mV]', color='C0')

                ax2 = ax.twinx()
                # plot frequency
                ax2.scatter(valid_time, valid_freq, color='orange', label='response: %s Hz' % response)
                ax2.set_ylabel('frequency [Hz]', color='orange')

                # plot fit
                # ax2.plot(valid_time[valid_time > 10], jar_fit_function(valid_time[valid_time > 10] - 10, *sv),
                #          color='black', label='sv: a1: %.2f, a2: %.2f, tau1: %.2f, tau2: %.2f'
                #                               % (sv[0], sv[1], sv[2], sv[3]))
                ax2.plot(valid_time[valid_time > 10], jar_fit_function2(valid_time[valid_time > 10] - 10, *sv2),
                         color='grey', label='sv2: a1: %.2f, tau1: %.2f'
                                             % (sv2[0], sv2[1]))

                plt.legend(loc='lower right')
                plt.title('%s, %s, %s, loop_%s' % (id, comment, key, idx))
                plt.show()

                # plt.savefig('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/jar_plots/%s/'
                #             '%s, %s, %s, loop_%s.png' % (dataset, k_str, id, comment, key, idx))
                plt.close()

            print('mean over taus:', np.mean(taus))

            jar_savepath = '/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/%s' % (dataset, k_str)
            np.save(jar_savepath + '/%s_jar.npy' % k_str, zip(taus, responses))

            # fitted tau1 takes whatever value near 0 put in
            print('-------------------------------------')
            os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

        embed()
