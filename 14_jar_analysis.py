import pandas as pd
from IPython import  embed
import numpy as np
from JAR_Functions import plot_alle_apteronoti_JAR, plot_alle_eigenmannia_JAR, plot_JAR_bodypara, plot_einzelne_Fische_JAR
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


#fig = plot_alle_eigenmannia_JAR(jar_eigen, df_eigen)



#Plot Apteronotus
#Frage - doppelte Medianpunkte raus bekommen??????

jar_apti = np.array(df.jar[df.species == "Apteronotus leptorhynchus"])
df_apti = np.array(df.df[df.species == "Apteronotus leptorhynchus"])


#fig = plot_alle_apteronoti_JAR(jar_apti, df_apti)



#Plot einzelner Fische JAR_Median gegen df

#fig = plot_einzelne_Fische_JAR(id, df)






#JAR-Höhe Korrelation mit Größe und Gewicht (Dominanz) Eigenmannia und Apteronoti getrennt

#Eigen

unique_ids_eigen = np.unique(df.id[df.species == 'Eigenmannia virescens' ])
embed()
quit()

#fig = plot_JAR_bodypara(unique_ids_eigen, df, specie = "E. virescens")
#fig.savefig('../results/Vortrag/Korrelation_JAR_Gewicht_Eigen.png')


#Apti

unique_ids_apti  = np.unique(df.id[df.species == 'Apteronotus leptorhynchus'])
fig = plot_JAR_bodypara(unique_ids_apti, df, specie = "A. leptorhynchus")
fig.savefig('../results/Vortrag/Korrelation_JAR_Gewicht_Apti.png')
#plt.show(plot_bodypara_apti)

plt.show()













