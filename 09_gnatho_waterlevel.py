# Einfacher plot der aufgezeichneten EOD
from nix_helpers import read_eod
from helper_functions import threshold_crossing
import numpy as np
import matplotlib.pyplot as plt




dataset = "../data/pulse/2020-12-15-ac-barometrix/2020-12-15-ac-barometrix.nix"
threshold = 1.9
snippet_times = []
snippet_eods = []
maxima_eodf = []
minima_eodf = []
amplitudes = []
eod_times = []

time, eodf = read_eod(dataset, duration=40)
eodf = eodf - np.median(eodf)
ceodftime = threshold_crossing(eodf, time, threshold)

#Zeitfenster um +- 0.001 erweitern
for et in ceodftime:
    start_time = et - 0.001
    end_time = et + 0.001
    snippet_time = time[(time >= start_time) & (time < end_time)]
    snippet_eod = eodf[(time >= start_time) & (time < end_time)]

    #Berechnen der Indices der Max und Mins der Funktion
    max_eod = np.argmax(snippet_eod)
    min_eod = np.argmin(snippet_eod)

    #Zugriff auf Zeitvektor und holen uns Elemente an zuvor berechneten Max und Min Stellen (Indices) + hinzufügen zu Liste
    snippet_time_max = snippet_time[max_eod]
    snippet_time_min = snippet_time[min_eod]
    eod_times.append((snippet_time_max + snippet_time_min) / 2)

    #Berechnen von Amplituden
    eodf_max = snippet_eod[max_eod]
    eodf_min = snippet_eod[min_eod]
    maxima_eodf.append(eodf_max)
    minima_eodf.append(eodf_min)
    amplitude = eodf_max - eodf_min
    amplitudes.append(amplitude)



#Frequenzberechnung - in Hz --> d.h. wie viele Ausschläge pro Sekunde --> wie viele Maxima pro Sekunde?; anderer Weg: 1/Zeitpunktdifferenz
difference = np.diff(eod_times)
frequency = 1 / difference
plt.plot(eod_times[:-1], frequency)

#plt.plot(frequency, amplitudes[:-1], 'o')
plt.xlabel("time [sec]")
plt.ylabel("frequency [Hz]")
fig1 = plt.gcf()
fig1.savefig('../results/gnatho/gnathonemus_petersii_changeinwaterlevel.pdf')
plt.show()

"""plt.hist(difference)"""

#plt.plot(time, eodf, color = "green" )
#plt.scatter(ceodftime, np.ones_like(ceodftime)*threshold)
#plt.show()
"""plt.plot(maxima, amplitudes, "o")"""
