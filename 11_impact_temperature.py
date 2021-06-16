import matplotlib.pyplot as plt
import numpy as np
from helper_functions import read_eod_frequency, read_temperature, read_species, calculate_q10
from nix_helpers import read_block_metadata, read_subject_info
import glob

# empty lists
temperatures = []
EODfs = []
Q10list = []

# load data
datasets = sorted(glob.glob("../data/JAR/2020-12-17*/*.nix"))

for dataset in datasets:
    temperature = read_temperature(dataset) #Temp. in Kelvin
    EODf = read_eod_frequency(dataset)
    temperatures.append(temperature)
    EODfs.append(EODf)

"""for i in range(len(temperatures)-1): #for-Schleife für i innerhalb von: len(temperatures)-1 --> Anzahl der Daten in Liste temperatures - 1 (damit Befehl ausführbar ist, wenn i+1 dran steht)
    temp1 = temperatures[i]
    temp2 = temperatures[i+1]
    EODf1 = EODfs[i]
    EODf2 = EODfs[i+1]
    if Q10 == 0.0
        continue
    Q10 = calculate_q10(EODf1, EODf2, temp1, temp2)"""

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

mean = np.mean(Q10list)
std = np.std(Q10list)
print('mean: ', mean)
print('std:', std)

#plt.boxplot(Q10list, sym='d', boxprops={'color': 'dodgerblue', 'lw': 2.5}, whis=[10, 90])
#plt.ylabel("Q10-value")
#fig1 =plt.gcf()
#fig1.savefig('../results/temperature/Q10_boxplot.pdf')
#plt.show()













"""plt.scatter(temperatures, EODfs)
plt.xlabel("Temperature[°C]", fontsize=10)
plt.ylabel("EODf [Hz]", fontsize=10)
plt.show()

# fig = plt.gcf()
#fig.set_size_inches(7, 5)
#fig.tight_layout()
#fig.savefig('../results/waterlevel/ampli_vs_level_'+ subject_id +'.pdf')
#plt.close()
"""
