import nixio as nix
import glob
import os
import numpy as np
import matplotlib.mlab as mlab
import pandas as pd
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
from main import data_finder

all_keys = [(-5.0, 0.0, False), (5.0, 0.0, False), (-50.0, 0.0, False), (50.0, 0.0, False), (-150.0, 0.0, False),
            (150.0, 0.0, False), (-150.0, 750.0, False), (150.0, 750.0, False), (-50.0, 0.0, True), (50.0, 0.0, True)]
chirp_keys = [(-50.0, 0.0, False), (-150.0, 750.0, False), (150.0, 750.0, False), (-150.0, 0.0, False),
              (150.0, 0.0, False), (50.0, 0.0, False)]
jar_keys = [(-5.0, 0.0, False), (5.0, 0.0, False)]
echo_keys = [(-50.0, 0.0, True), (50.0, 0.0, True)]


def main():
    global all_keys
    datafolder = '/home/localadmin/data/electricbehaviour/recordings'
    datasets = data_finder(datafolder)

    df = pd.DataFrame(columns=['id', 'daytime', 'deltaf', 'fakefish', 'generate_chirps', 'time_constant',
                               'deltaf_response', 'number_chirps', 'number_bigchirps', 'response_ratio'])

    for dataset in datasets:
        dataset = dataset[-17:-4]
        print(dataset)
        os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)
        if dataset == '2021-03-16-ae':
            all_keys = [(-5.0, 0.0, False), (5.0, 0.0, False), (-50.0, 0.0, False), (50.0, 0.0, False),
                        (-150.0, 0.0, False), (150.0, 0.0, False), (-150.0, 750.0, False), (150.0, 750.0, False)]
        if dataset == '2021-03-16-af':
            all_keys = [(-50.0, 0.0, True), (50.0, 0.0, True)]

        for key in all_keys:

            if key[0] == -5 or key[0] == 5:
                print('jar')
                k_str = str(key).replace(' ', '')
                print(k_str)
                load_key = np.load('%s_key.npy' % k_str)

                os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/%s' % (dataset, load_key))

                data = np.load('%s_data.npy' % load_key, allow_pickle=True)
                id = data[0]
                daytime = data[1]
                deltaf = data[2].split(',')[0][1:]
                fakefish = data[2].split(',')[1]
                generate_chirps = data[2].split(',')[2][:-1]
                time_constant = data[3]
                deltaf_response = data[4]

                row = {'id': id, 'daytime': daytime, 'dataset': dataset, 'deltaf': deltaf, 'fakefish': fakefish,
                       'generate_chirps': generate_chirps, 'time_constant': time_constant,
                       'deltaf_response': deltaf_response}
                for k in df.keys():
                    if k not in row.keys():
                        row[k] = None
                df = df.append(row, ignore_index=True)
                os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

            if key[2] is True:
                print('echo')
                k_str = str(key).replace(' ', '')
                print(k_str)
                load_key = np.load('%s_key.npy' % k_str)

                os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/%s' % (dataset, load_key))

                data = np.load('%s_data.npy' % load_key, allow_pickle=True)
                id = data[0]
                daytime = data[1]
                deltaf = data[2].split(',')[0][1:]
                fakefish = data[2].split(',')[1]
                generate_chirps = data[2].split(',')[2][:-1]
                response_ratio = data[3]

                row = {'id': id, 'daytime': daytime, 'dataset': dataset, 'deltaf': deltaf, 'fakefish': fakefish,
                       'generate_chirps': generate_chirps, 'response_ratio': response_ratio}
                for k in df.keys():
                    if k not in row.keys():
                        row[k] = None
                df = df.append(row, ignore_index=True)
                os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

            if key[2] is False and key[0] != 5 and key[0] != -5:
                print('chirp')
                k_str = str(key).replace(' ', '')
                print(k_str)
                load_key = np.load('%s_key.npy' % k_str)

                os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/%s' % (dataset, load_key))

                data = np.load('%s_data.npy' % load_key, allow_pickle=True)

                id = data[0]
                daytime = data[1]
                deltaf = data[2].split(',')[0][1:]
                fakefish = data[2].split(',')[1]
                generate_chirps = data[2].split(',')[2][:-1]
                number_chirps = data[3]
                number_bigchirps = data[4]

                row = {'id': id, 'daytime': daytime, 'dataset': dataset, 'deltaf': deltaf, 'fakefish': fakefish,
                       'generate_chirps': generate_chirps, 'number_chirps': number_chirps,
                       'number_bigchirps': number_bigchirps}
                for k in df.keys():
                    if k not in row.keys():
                        row[k] = None
                df = df.append(row, ignore_index=True)
                os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)

        all_keys = [(-5.0, 0.0, False), (5.0, 0.0, False), (-50.0, 0.0, False), (50.0, 0.0, False),
                    (-150.0, 0.0, False),
                    (150.0, 0.0, False), (-150.0, 750.0, False), (150.0, 750.0, False), (-50.0, 0.0, True),
                    (50.0, 0.0, True)]

    df = df.sort_values(['id', 'daytime'], ignore_index=True)
    print(df.to_string())
    embed()
    quit()


if __name__ == '__main__':
    main()