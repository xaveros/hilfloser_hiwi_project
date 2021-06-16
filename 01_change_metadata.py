from nix_helpers import read_eod, read_jar_data
from helper_functions import read_eod_frequency, threshold_crossing, read_species
import matplotlib.pyplot as plt
import numpy as np
import glob
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
mean_fs = []
dfs = []

#weise Variable dataset Dateipfad zu
#dataset = '../data/JAR/2020-12-17-ac-electrophorus/2020-12-17-ac-electrophorus.nix'
datasets = sorted(glob.glob("../data/JAR/2020-12-17*/*.nix")) #- Frage: wie kann ich 2020-12-21


for dataset in datasets:

    species, id = read_species(dataset)
    print (species)
    if species == 'Apteronotus leptorhynchus':
        embed()
        quit()