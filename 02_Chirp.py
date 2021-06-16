import matplotlib.pyplot as plt
from helper_functions import read_eod_frequency, threshold_crossing
import numpy as np
import nix_helpers as nx
import glob

dfs = []
ceodftimes = []
frequencies = []
chirp_times_list = []

datasets = sorted(glob.glob("../data/stimulation_att/2020-12-22*/*.nix"))

for dataset in datasets:
    # Funktion read_jar_data, gibt time eod und delta f zurück - passt hier auch oder nur df?
    time, eod, df = nx.read_jar_data(dataset)

    # liest eod frequency und gibt eodf zurück (frequency), um Periode zu berechnen
    eodf = read_eod_frequency(dataset)

    # überschreiben von eod mit eod - Median von eod (als Mittelung?)
    eod = eod - np.median(eod)
    threshold = 0.25

    # erstellen von Kopie von eodf_time, dann anwenden von Funktion --> ergibt 2 überlappende Funktionen, um eod rauszufinden
    ceodftime = threshold_crossing(eod, time, threshold)
    if len(ceodftime) < 1:
        continue
    ceodftimes.append(ceodftime)

    # EOD_Periode berechnen
    eod_period = 1/eodf
    segment_duration = 1.25 * eod_period

    difference = np.diff(ceodftime)
    frequency = 1 / difference
    frequency = frequency - np.mean(frequency)
    kernel = np.ones(10)/10
    better_frequencies = np.convolve(kernel, frequency,  mode='same')

    frequencies.append(better_frequencies)

    #threshold setzen, um nur Chirps zu detektieren
    threshold = 50
    chirp_times = threshold_crossing(better_frequencies, ceodftime[:-1], threshold)
    chirp_times_list.append(len(chirp_times))
    dfs.append(np.round(df))
    #Anzahl Chirps
    #print(len(chirp_times))


dfs_array = np.asarray(dfs)
chirp_counts_array = np.asarray(chirp_times_list)

unique_dfs = np.unique(dfs_array)
#print(unique_dfs)
mean_chirp_counts = []
for udf in unique_dfs:
    mean_chirp_counts.append(np.mean(chirp_counts_array[np.abs(dfs_array - udf) < 2.5]))

#brauchen wir gerade nicht mehr:
plt.plot(ceodftimes[:-1], better_frequencies, label=str(np.round(df,0)))
#plt.plot(chirp_times, np.ones_like(chirp_times) * threshold)
plt.scatter(dfs, chirp_times_list)
plt.scatter(unique_dfs, mean_chirp_counts, c = 'red')
plt.legend()
plt.show()

