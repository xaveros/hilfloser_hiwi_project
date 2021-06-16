import numpy as np
from nix_helpers import read_block_metadata, read_eod, read_subject_info
from IPython import embed


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def cut_segments(time, data, segment_length):
    """
    cuts segments in defined lengths and returns them.
    :param time: vector with time entries
    :param data: vector with data entries
    :param segment_length: duration of a segment in seconds
    :return: list of segments
    """
    segments = []
    max_duration = time[-1]
    segment_count = int(np.floor(max_duration / segment_length))
    for i in range(segment_count):
        segment = data[(time >= segment_length * i) & (time < segment_length * (i + 1))]
        segments.append(segment)

    return segments

def calculate_amplitudes(segments):
    """
    calculates amplitudes and returns them
    :param segments: list of segments
    :return: list of amplitudes
    """
    amplitudes = []
    for segment in segments:
        segment_max = np.max(segment)
        segment_min = np.min(segment)
        segment_amplitude = segment_max - segment_min
        amplitudes.append(segment_amplitude)

    return amplitudes

def read_waterlevel(dataset):
    """
    Get info/metadata and read waterlevel
    :param dataset: list of data
    :return: value of waterlevel in cm
    """
    waterlevel = 0.0
    metadata = read_block_metadata(dataset)
    waterlevel = metadata["Recording"] ["WaterLevel"] [0]
    return waterlevel

def read_eod_amplitude(dataset, segment_length=0.05):
    """
    read median of amplitudes out of list of data.
    :param dataset: list of data
    :param segment_length: length of a segment in seconds
    :return: median of one set of amplitudes
    """
    time, eod = read_eod(dataset, 30)
    segments = cut_segments(time, eod, segment_length)
    ampls = calculate_amplitudes(segments)
    return np.median(ampls)

def read_species(data):
    """
    Get speciesname and ID our of metadata
    :param data: list of data
    :return: name of species and ID
    """
    species = read_subject_info(data)
    speciesname = species["Species"][0]
    if "Identifier" in species.keys():

        ID = species["Identifier"][0]
    else:
        ID = species["Individual Name"][0]
    return speciesname, ID

def read_body_parameter(data):
    """
    Get speciesname and ID our of metadata
    :param data: list of data
    :return: name of species and ID
    """
    species = read_subject_info(data)
    weight = None
    size = None
    if "Weight" in species.keys():
        weight = float(species["Weight"][0])
    if 'Size' in species.keys():
        size = float(species["Size"][0])
    return weight, size

def read_eod_frequency(data):
    info = read_subject_info(data)
    eodf = np.round(info["EOD Frequency"][0], 2)
    return eodf

def read_temperature(data):
    metadata = read_block_metadata(data)
    watertemp = metadata["Recording"]["WaterTemperature"][0] #Kelvin rausrechnen

    if type(watertemp) == str:
        if is_number(watertemp):
            watertemp = float(watertemp)
        else:
            embed()
    watertemp = np.round(watertemp - 273.15, 2)

    return watertemp

def calculate_q10(frequency1, frequency2, watertemp1, watertemp2):
    """if watertemp1 > watertemp2:
        watertemp1, watertemp2 = watertemp2, watertemp1
        frequency1, frequency2 = frequency2, frequency1"""

    if watertemp1 == watertemp2:
        """print("Keine Temperaturdifferenz feststellbar, Ausgabe von Q10-Wert nicht möglich")"""
        return 0.0


    Q10 = (frequency2 / frequency1) ** (10 / (watertemp2 - watertemp1))

    return Q10

def threshold_crossing(data, time, threshold):
    cdata = np.roll(data, 1)
    times = time[(data > threshold) & (cdata <= threshold)]
    return times

