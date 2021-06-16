#daten finden
    #einzelne datensätze laden
        #metadata
            #stimulusposition
            #messposition
            #temp, leitfähigkeit
        #amplitude
        #stimulusfrequenz
#plotten: heatmap

import nixio as nix
import glob
import os
import numpy as np
import matplotlib.mlab as mlab
import pandas
import matplotlib.pyplot as plt
from IPython import embed

def data_finder(folder):
    datasets = sorted(glob.glob(os.path.join(folder, '2021*', '*.nix')))
    return datasets

def analysis_dataset(dataset):
    nf = nix.File.open(dataset, nix.FileMode.ReadOnly)
    b = nf.blocks[0]
    embed()
    quit()
    metadata = load_metadata(b)
    metadata['amplitude'] = load_amplitude(b)

    nf.close()

    return metadata

def load_metadata(b):    #stimulus- und messelektrodenposition, temp & leitfähigkeit,
    if 'StimulusAPositionX' in b.metadata['Recording']:
        Stim_A_X = b.metadata['Recording']['StimulusAPositionX']
        Stim_A_Y = b.metadata['Recording']['StimulusAPositionY']
    Stim_B_X = 0
    Stim_B_Y = 0
    if 'StimulusBPositionX' in b.metadata['Recording']:
        Stim_B_X = b.metadata['Recording']['StimulusBPositionX']
        Stim_B_Y = b.metadata['Recording']['StimulusBPositionY']

    if 'StimulusPositionX' in b.metadata['Recording']:
        Stim_A_X = b.metadata['Recording']['StimulusPositionX']
        Stim_A_Y = b.metadata['Recording']['StimulusPositionY']

    measure_x = b.metadata['Recording']['MeasurementX']
    measure_y = b.metadata['Recording']['MeasurementY']

    temp = np.round(b.metadata['Recording']['WaterTemperature'] - 273.15, 1)
    conduct = b.metadata['Recording']['WaterConductivity']
    
    metadata = {'measure_x': measure_x, 'measure_y': measure_y,
            'stim_a_x': Stim_A_X, 'stim_a_y': Stim_A_Y, 'stim_b_x': Stim_B_X,
            'stim_b_y': Stim_B_Y, 'temperature': temp, 'conductivity': conduct}
    
    return metadata

def load_amplitude(b):
    mt = b.multi_tags[0]
    eod = mt.retrieve_data(len(mt.positions)-1, 'EOD-1')

    p, f = mlab.psd(eod, Fs=20000, NFFT=2**14, noverlap=2**13, detrend='mean')

    df = np.mean(1 / np.diff(f))

    i = np.sum(p[(f < 675) & (f > 625)]) * df
    amplitude = np.sqrt(i)
    return amplitude

def load_stimulus_frequency():

    pass


def main():
    datafolder = '/home/efish/data/ymaze/1fakefish-ISO_A'
    datasets = data_finder(datafolder)

    measurements_x = []
    measurements_y = []
    amplitudes = []

    df = None
    results = []
    for dataset in datasets:
        results.append(analysis_dataset(dataset))


    df = pandas.DataFrame(results)

    piv = pandas.pivot_table(df, values="amplitude", index=["measure_y"], columns=["measure_x"], fill_value=0)
    fig, ax = plt.subplots(figsize=(6, 6))

    ax.imshow(piv, interpolation='bilinear', extent=[0, 110, 0, 40])
    ax.set_xlabel('x [cm]')
    ax.set_ylabel('y [cm]')
    plt.show()
    embed()
    quit()


if __name__ == '__main__':
    main()
