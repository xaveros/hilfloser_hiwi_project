import pandas as pd
from IPython import  embed
import numpy as np
import matplotlib.pyplot as plt
from helper_functions import calculate_q10

df = pd.read_csv('jar_features.csv', sep=';', index_col=0)

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




#Musterjar - Plot --> aus JAR holen/ von Phillip

#Jar Plot, pro Spezies einer
#was wir dafür brauchen: JAR gegen df aufgetragen in Scatter plot

#Plot Eigenmannia

jar_eigen = np.array(df.jar[df.species == "Eigenmannia virescens"])

df_eigen = np.array(df.df[df.species == "Eigenmannia virescens"])



unique_dfs_eigen = np.unique(df_eigen)
jar_eigen_median = []
for udf in unique_dfs_eigen:

    jar_eigen_median.append(np.median(jar_eigen[np.abs(df_eigen - udf) < 2.5]))

plt.scatter(df_eigen, jar_eigen)
plt.scatter(unique_dfs_eigen, jar_eigen_median, color = 'r')
plt.plot([-35, 35], [0,0], c='black', ls='--')
plt.plot([0, 0], [-15, 15], c='black', ls='--')
plt.xlim([-35, 35])
plt.ylim([-15, 15])
plt.ylabel("response [HZ]")
plt.xlabel("delta F [Hz]")
plt.title("JAR Eigenmannia virescens")

fig = plt.gcf()
fig.savefig('../results/Vortrag/eigenmannia_medianJAR_df.pdf')
plt.show()


#Plot Apteronotus


#Frage - doppelte Medianpunkte raus bekommen??????
jar_apti = np.array(df.jar[df.species == "Apteronotus leptorhynchus"])
df_apti = np.array(df.df[df.species == "Apteronotus leptorhynchus"])

unique_dfs_apti = np.unique(df_apti)
jar_apti_median =  []
for udf in unique_dfs_apti:

    jar_apti_median.append(np.median(jar_apti[np.abs(df_apti - udf) < 2.5]))

plt.scatter(df_apti, jar_apti)
plt.scatter(unique_dfs_apti, jar_apti_median, color = 'r')
plt.plot([-35, 35], [0,0], c='black', ls='--')
plt.plot([0, 0], [-10, 15], c='black', ls='--')
plt.xlim([-35, 35])
plt.ylim([-10, 15])
plt.ylabel("response [HZ]")
plt.xlabel("delta F [Hz]")
plt.title("JAR Apteronotus leptorhynchus")
fig = plt.gcf()
fig.savefig('../results/Vortrag/apteronotus_medianJAR_df.pdf')
tplt.show()





#Plot einzelner Fische JAR_Median gegen df

unique_ids = np.unique(id)
for ids in unique_ids:
    jar_eigen = np.array(df.jar[df.id == ids])

    df_eigen = np.array(df.df[df.id == ids])

    unique_dfs_eigen = np.unique(df_eigen)
    jar_eigen_median = []
    for udf in unique_dfs_eigen:

        jar_eigen_median.append(np.median(jar_eigen[np.abs(df_eigen - udf) < 2.5]))

    plt.scatter(df_eigen, jar_eigen)
    plt.scatter(unique_dfs_eigen, jar_eigen_median, color = 'r')
    plt.plot([-35, 35], [0,0], c='black', ls='--')
    plt.plot([0, 0], [-15, 15], c='black', ls='--')
    plt.xlim([-35, 35])
    plt.ylim([-15, 15])
    plt.ylabel("response [HZ]")
    plt.xlabel("delta F [Hz]")
    plt.title(ids)
    fig = plt.gcf()
    fig.savefig('../results/Vortrag/'+ ids +'_medianJAR_df.pdf')
    plt.show()





#JAR-Höhe Korrelation mit Größe und Gewicht (Dominanz) Eigenmannia und Apteronoti getrennt

unique_ids_eigen = np.unique(df.id[df.species == 'Eigenmannia virescens' ])
unique_ids_apti  = np.unique(df.id[df.species == 'Apteronotus leptorhynchus'])



for ids in unique_ids_eigen:
    jar_eigen = np.array(df.jar[df.id == ids])

    df_eigen = np.array(df.df[df.id == ids])

    weight_eigen = np.unique(df.weight[df.id == ids]) [0]
    size_eigen = np.unique(df['size'][df.id == ids])

    unique_dfs_eigen = np.unique(df_eigen)
    jar_eigen_median = []
    for udf in unique_dfs_eigen:

        jar_eigen_median.append(np.median(jar_eigen[np.abs(df_eigen - udf) < 2.5]))


    plt.plot(unique_dfs_eigen, jar_eigen_median, label = '%.1fg, %.1fcm'%(weight_eigen, size_eigen))
    plt.legend()
    plt.plot([-35, 35], [0, 0], c='black', ls='--')
    plt.plot([0, 0], [-8, 10], c='black', ls='--')
    plt.xlim([-35, 35])
    plt.ylim([-8, 10])
    plt.ylabel("response [HZ]")
    plt.xlabel("delta F [Hz]")
    plt.title('Korrelation zwischen JAR [Hz] und Gewicht [g]')
    fig = plt.gcf()
    fig.savefig('../results/Vortrag/Korrelation_JAR_Gewicht_Eigen.pdf')
plt.show()


for ids in unique_ids_apti:
    jar_eigen = np.array(df.jar[df.id == ids])

    df_eigen = np.array(df.df[df.id == ids])

    weight_eigen = np.unique(df.weight[df.id == ids]) [0]
    size_eigen = np.unique(df['size'][df.id == ids])

    unique_dfs_eigen = np.unique(df_eigen)
    jar_eigen_median = []
    for udf in unique_dfs_eigen:

        jar_eigen_median.append(np.median(jar_eigen[np.abs(df_eigen - udf) < 2.5]))


    plt.plot(unique_dfs_eigen, jar_eigen_median, label = '%.1fg, %.1fcm'%(weight_eigen, size_eigen))
    plt.legend()
    plt.plot([-35,35], [0,0], c = 'black', ls = '--')
    plt.plot([0,0], [-2, 12], c= 'black', ls = '--')
    plt.xlim([-35, 35])
    plt.ylim([-2, 12])
    plt.ylabel("response [HZ]")
    plt.xlabel("delta F [Hz]")
    plt.title('Korrelation zwischen JAR [Hz] und Gewicht [g]')
    fig = plt.gcf()
    fig.savefig('../results/Vortrag/Korrelation_JAR_Gewicht_Apti.pdf')
plt.show()








