#Einfluss Wasserhöhe auf Feldamplitude der elektrischen Fischen
# assemble list of datasets
# for each dataset:
#   read the waterlevel from metadata -> add to waterlevel list
#   read amplitudes:
#       load data
#       cut to pieces
#       calculate amplitudes
#       calculate median -> add to amplitudes list

import matplotlib.pyplot as plt
import numpy as np
from helper_functions import read_waterlevel, read_eod_amplitude, read_species
from nix_helpers import read_eod, read_block_metadata
import glob


def plot_single_subject_data(datasets, subject_id):
    waterlevels = []
    amplitudes = []
    for dataset in datasets:
        waterlevel = read_waterlevel(dataset)
        amplitude = read_eod_amplitude(dataset)
        specie, identifier = read_species(dataset)
        if subject_id != identifier:
            continue
        waterlevels.append(waterlevel)
        amplitudes.append(amplitude)

    # Ziel: Plot Amplituden versus Wasserhöhe
    plt.scatter(waterlevels, amplitudes)
    plt.xlabel("Waterlevel [cm]", fontsize=10)
    plt.ylabel("Amplitude [mV]", fontsize=10)
    fig = plt.gcf()
    fig.set_size_inches(7, 5)
    fig.tight_layout()
    fig.savefig('../results/waterlevel/ampli_vs_level_'+ subject_id +'.pdf')
    plt.close()


datasets = sorted(glob.glob("../data/wave/2020-12-08*/*.nix"))
subject_ids = ["2013eigen13", "2020albi02"]

for subject_id in subject_ids:
    plot_single_subject_data(datasets, subject_id)


