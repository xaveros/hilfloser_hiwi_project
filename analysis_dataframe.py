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

all_keys = [(-50.0, 0.0, False), (-150.0, 750.0, False), (150.0, 750.0, False), (-150.0, 0.0, False),
            (150.0, 0.0, False), (50.0, 0.0, False), (-5.0, 0.0, False), (5.0, 0.0, False), (-50.0, 0.0, True),
            (50.0, 0.0, True)]
chirp_keys = [(-50.0, 0.0, False), (-150.0, 750.0, False), (150.0, 750.0, False), (-150.0, 0.0, False),
              (150.0, 0.0, False), (50.0, 0.0, False)]
jar_keys = [(-5.0, 0.0, False), (5.0, 0.0, False)]
echo_keys = [(-50.0, 0.0, True), (50.0, 0.0, True)]


def main():
    datafolder = '/home/localadmin/data/electricbehaviour/recordings'
    datasets = data_finder(datafolder)

    df = pd.DataFrame(columns=['id', 'daytime', 'deltaf', 'fakefish', 'generate_chirps', 'deltaf_response',
                               'time_constant', 'number_chirps', 'number_bigchirps', 'response_ratio'])

    for dataset in datasets:
        dataset = dataset[-17:-4]
        print(dataset)
        os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/keys' % dataset)
        print(os.getcwd())
        for key in all_keys:

            print(key)

            if key[0] == -5 or key[0] == 5:
                k_str = str(key).replace(' ', '')
                load_key = np.load('%s_key.npy' % k_str)

                os.chdir('/home/localadmin/PycharmProjects/hilfloser_hiwi_project/saves/%s/%s' % (dataset, load_key))

                data = np.load('%s_data.npy' % load_key, allow_pickle=True)
                id = data[0]
                daytime = data[1]
                deltaf = data[2].split(',')[0][1:]
                fakefish = data[2].split(',')[1]
                generate_chirps = data[2].split(',')[0][-4:]
                deltaf_response = data[3]
                time_constant = data[4]

                row = {'id': id, 'daytime': daytime, 'deltaf': deltaf, 'fakefish': fakefish,
                       'generate_chirps': generate_chirps, 'deltaf_response': deltaf_response,
                       'time_constant': time_constant}
                for k in df.keys():
                    if k not in row.keys():
                        row[k] = None
                df = df.append(row, ignore_index=True)
            print(df)
        embed()
        quit()


if __name__ == '__main__':
    main()