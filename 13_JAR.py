from nix_helpers import read_eod, read_jar_data
from helper_functions import read_eod_frequency, read_species, read_body_parameter,read_temperature
import matplotlib.pyplot as plt
import numpy as np
import glob
import pandas as pd
from detect_eod import detect_eod_times
from IPython import embed

#Zugriff auf delta f aus Metadaten
#Zugriff auf Frequenz von Fischi aus Metadaten (wo steht die?)
#Plotten von Frequenz von JAR [Fischi Frequenz - Ausgangsfrequenz Fisch] (Y-Achse) gegen delta F (X-Achse)

#leere Listen
snippet_times = []
snippet_eods = []
maxima_eodf = []

minima_eodf = []
eod_times = []
median_fs = []
dfs = []

#weise Variable dataset Dateipfad zu
#datasets = '../data/JAR/2020-12-21-at-majestix/2020-12-21-at-majestix.nix'
datasets = sorted(glob.glob("../data/JAR/*/*.nix")) #- Frage: wie kann ich 2020-12-21
#datasets = sorted(glob.glob("../data/JAR/2020-12-21*/*.nix"))


features = {'dataset': [], 'id': [], 'species': [], 'df': [], 'eodf': [], 'size': [], 'weight': [], 'jar': [], 'watertemperature': []}
thresholds = {'barometrix': 0.0}

for dataset in datasets:
    watertemperature = read_temperature(dataset)
    specie, ID = read_species(dataset)
    weight, size = read_body_parameter(dataset)
    #Funktion read_jar_data, gibt time eod und delta f zurück
    time, eod, df = read_jar_data(dataset)

    #liest eod frequency und gibt eodf zurück (frequency), um Periode zu berechnen
    eodf = read_eod_frequency(dataset)

    if watertemperature != 25:
        eodf_genormt = eodf * 1.6 **((25 - watertemperature)/10)
    else:
        eodf_genormt = eodf

    #überschreiben von eod mit eod - Median von eod (um auf 0 zu bringen)


    eod  = eod - np.median(eod)
    #threshold = 0.0

    times, idx = detect_eod_times(time, eod)


    #erstellen von Kopie von eodf_time, dann anwenden von Funktion --> ergibt 2 überlappende Funktionen, um eod rauszufinden
    #ceodftime = threshold_crossing(eod, time, threshold)

    #EOD_Periode berechnen
    eod_period = 1/eodf
    segment_duration = 1.25 * eod_period

    difference = np.diff(times)
    frequency = 1 / difference
    frequency = frequency - eodf
    # kernel = np.ones(5)/5
    # better_frequencies = np.convolve(kernel, frequency,  mode = 'same')
    median_f = np.median(frequency[times[:-1] > 15])




    # print(dataset)
    #print(watertemperature)

    dfs.append(df)
    median_fs.append(median_f)
    features['dataset'].append(dataset)
    features['species'].append(specie)
    features['id'].append(ID)
    features['df'].append(np.round(df))
    features['eodf'].append(eodf_genormt)
    features['size'].append(size)
    features['weight'].append(weight)
    features['jar'].append(median_f)
    features['watertemperature'].append(watertemperature)

    print(dataset)
df = pd.DataFrame(features)
df.to_csv('jar_features_Q10genormt.csv', sep=';')
#plt.scatter(dfs, mean_fs, label=str(np.round(df,0)))
#plt.legend()
#plt.show()








"""
#Temperatur normen

for i in range(len(temperatures)): #super intelligente Schleife zum paaren der Daten, jeder mit jedem - außer mit sich selbst und auch nicht doppelt
    for j in range(len(temperatures)):
        if i < j:
            temp1 = temperatures[i]
            temp2 = temperatures[j]
            EODf1 = EODfs[i]
            EODf2 = EODfs[j]
            Q10 = calculate_q10(EODf1, EODf2, temp1, temp2)

    if Q10 == 0.0:
        continue

    Q10list.append(Q10)
#Brauchen wir überhaupt 100000 Q10 Werte, wollten die ja nur überprüfen und sind ca. gleich groß (meistens - 1.5/1.6)
#Q10-Wert dann mit EOD verrechnen







plt.plot(time, eod)
plt.plot(df, color="green")
plt.xlabel("time in s")
plt.ylabel("eod in mV")
plt.show()



    eodf_max = snippet_eod[max_eod]
    eodf_min = snippet_eod[min_eod]
    maxima_eodf.append(eodf_max)
    minima_eodf.append(eodf_min)
    amplitude = eodf_max - eodf_min
    amplitudes.append(amplitude)



for et in ceodftime:#liest eod frequency und gibt eodf zurück (frequency), um Periode zu berechnen
eodf = read_eod_frequency(dataset)

#überschreiben von eod mit eod - Median von eod (als Mittelung?)
eod = eod - np.median(eod)
threshold = 1.9

#erstellen von Kopie von eodf_time, dann anwenden von Funktion --> ergibt 2 überlappende Funktionen, um eod rauszufinden
ceodftime = threshold_crossing(eod, time, threshold)

#EOD_Periode berechnen
eod_period = 1/eodf
segment_duration = 1.25 * eod_period
    start_time = et - segment_duration/2
    end_time = et + segment_duration/2
    snippet_time = time[(time >= start_time) & (time < end_time)]
    snippet_eod = eod[(time >= start_time) & (time < end_time)]

    #Berechnen der Indices der Max und Mins der Funktion
    max_eod = np.argmax(snippet_eod)
    min_eod = np.argmin(snippet_eod)

    #Zugriff auf Zeitvektor und holen uns Elemente an zuvor berechneten Max und Min Stellen (Indices) + hinzufügen zu Liste
    snippet_time_max = snippet_time[max_eod]
    snippet_time_min = snippet_time[min_eod]
    eod_times.append((snippet_time_max + snippet_time_min) / 2)
"""