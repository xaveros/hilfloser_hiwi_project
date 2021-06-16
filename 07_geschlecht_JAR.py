from IPython import  embed
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from helper_functions import calculate_q10

df = pd.read_csv('jar_features_Q10genormt.csv', sep=';', index_col=0)

#alles in np.array konvertieren
id = np.array(df.id)
species = np.array(df.species)
watertemperature = np.array(df.watertemperature)
dataset = np.array(df.dataset)
delta_f = np.array(df.df)
eodf = np.array(df.eodf) #eodf nicht mit Q10 genormt, ist in anderer CSV Datei!
bodysize = np.array(df['size'])
weight = np.array(df.weight)
jar = np.array(df.jar)

inch = 2.54
fs = 22
plt.rcParams['font.size']=17
plt.rc('xtick', labelsize=17)
plt.rc('ytick', labelsize=17)

# Korrelation JAR mit Geschlecht bei Apti??
#Theorie: 600-800 Hz --> weibl. 800-1000 Hz --> männlich

#eodf = df.eodf[species == "Apteronotus leptorhynchus"]


#ids = df.id[species == "Apteronotus leptorhynchus"]

#unique_ids = np.unique(ids)

fig, ax = plt.subplots(1, 1, figsize=(30 / inch, 20 / inch))
fig.subplots_adjust(left=0.1, bottom=0.1, right=0.96, top=0.9)

unique_ids = ['2020lepto49', '2020lepto04', '2020lepto06', '2018lepto76', '2019lepto27']

for i in unique_ids:

    jar = np.array(df.jar[df.id == i])

    dfs = np.array(df.df[df.id == i])

    eodfs = np.median(df.eodf[df.id == i])

    unique_dfs = np.unique(dfs)

    jar_median = []
    for udf in unique_dfs:
        jar_median.append(np.median(jar[np.abs(dfs - udf) < 2.5]))
    ax.plot(unique_dfs, jar_median, marker='', label='%.1fHz' % (eodfs))
plt.legend(loc='lower left')
ax.plot([-35, 35], [0, 0], c='black', ls='--')
ax.plot([0, 0], [-8, 12], c='black', ls='--')
ax.plot([0, 35], [0, 35], c='gray', ls='--')
ax.set_xlim([-35, 35])
ax.set_ylim([-8, 12])
ax.set_ylabel("response [Hz]", fontsize=fs)
ax.set_xlabel("delta F [Hz]", fontsize=fs)
#ax.set_title('Korrelation zwischen JAR [Hz] und Grundfrequenz [Hz]', fontsize = fs)

#embed()
fig.savefig('../results/Vortrag/Korrelation_JAR_Eodf_Apti.png')
plt.show()
