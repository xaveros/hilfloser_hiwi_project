# JAR
    # load data
    # norm data
    # mean over traces
    # filter
    # fit --> time constant

import nixio as nix
import glob
import os
import numpy as np
import matplotlib.mlab as mlab
import pandas
import matplotlib.pyplot as plt
from IPython import embed
from detect_eod import detect_eod_times
from scipy.optimize import curve_fit
from analysis import jar_analysis
from analysis import filter_data
from analysis import norm_data
from analysis import mean_traces_data
from analysis import jar_fit_function
from analysis import chirp_analysis

def data_finder(folder):
    path = (folder + '/*/*.nix')
    datasets = sorted(glob.glob(path))
    return datasets


def load_data_dictionary(dataset):

    nf = nix.File.open(dataset, nix.FileMode.ReadOnly)
    b = nf.blocks[0]

    # dictionary for tags
    tag_count = {}
    for t in b.tags:
        # fill tag dictionary with tag as key, if fakefish on or not, chirps on or not as values for each key
        tag_count[t.id] = (t.metadata['RePro-Info']['settings']['fakefish'],
                           t.metadata['RePro-Info']['settings']['generatechirps'])

    # dictionary for multi_tags to get df
    mt_dict = {}
    for mt in b.multi_tags:
        # enumerate mt.positions for number of tags in recording
        for index, _ in enumerate(mt.positions[:]):
            # multi_tag id

            tag_id = mt.features[mt.name + '_repro_tag_id'].data[index][0] #.decode()
            # read df
            if mt.name + '_DeltaF' in mt.features:
                df = mt.features[mt.name + '_DeltaF'].data[index][0]
            else:
                df = mt.metadata[mt.name]['DeltaF']
            # dict with key consisting of: df, fakefish/not fakefish, chirps/not chirps
            key = (df, tag_count[tag_id][0], tag_count[tag_id][1])
            # append id and tag position for each key
            if key in mt_dict.keys():
                mt_dict[key].append((mt.id, index))
            else:
                mt_dict[key] = [(mt.id, index)]
    return mt_dict


def load_id(dataset):
    os.chdir(dataset[:-18])

    ids = []
    with open('info.dat') as info:
        content = info.readlines()
        for c in content:
            if '#' and 'Identifier' in c:
                i = c.strip().split(':')[-1][2:-1]
                ids.append(i)
    id = ids[0]
    return id


def load_comment(dataset):
    os.chdir(dataset[:-18])

    comments = []
    with open('info.dat') as info:
        content = info.readlines()
        for c in content:
            if '#' and 'Comment' in c:
                i = c.strip().split(':')[-1][2:-1]
                comments.append(i)
    return comments


def main():
    # SAVE OR NOT SAVE?
    datafolder = '/home/localadmin/data/electricbehaviour/recordings'
    datasets = data_finder(datafolder)

    # print(datasets)
    for idx, dataset in enumerate(datasets):
        '''loaded:
        03-11-ab, 03-15-aa, 03-15-ab, 03-15-ac, 03-15-ae, 06-02-aa, 06-02-ab, 06-02-ac 
        next: zu allen geladenen JAR nochmal (erste fünf sind durch), 03-16-ag vollständig'''
        if idx == 17:   # new_recordings: idx 15-17
            id = load_id(dataset)
            day_time = load_comment(dataset)
            print(dataset)

            dataset_dict = load_data_dictionary(dataset)

            # chirp_keys = [(150.0, 750.0, False), (-150.0, 0.0, False), (150.0, 0.0, False), (50.0, 0.0, False),
            #               (-150.0, 750.0, False), (-50.0, 0.0, False)]
            # chirp_analysis(dataset, dataset_dict, chirp_keys, id)

            jar_keys = [(-5.0, 0.0, False), (5.0, 0.0, False)]
            jar_analysis(dataset, dataset_dict, jar_keys)

            echo_keys = [(-50.0, 0.0, True), (50.0, 0.0, True)]
            chirp_analysis(dataset, dataset_dict, echo_keys, id)

if __name__ == '__main__':
    main()