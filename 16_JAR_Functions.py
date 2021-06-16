from IPython import  embed
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from helper_functions import calculate_q10

inch = 2.45
fs  = 20
x = 30
y = 20
plt.rcParams['font.size']=17
plt.rc('xtick', labelsize=20)
plt.rc('ytick', labelsize=20)

def plot_alle_eigenmannia_JAR(jar_eigen, df_eigen):

    unique_dfs_eigen = np.unique(df_eigen)
    jar_eigen_median = []
    fig, ax = plt.subplots(1, 1, figsize=(x / inch, y / inch))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.96, top=0.9)

    for udf in unique_dfs_eigen:
        jar_eigen_median.append(np.median(jar_eigen[np.abs(df_eigen - udf) < 2.5]))

    ax.scatter(df_eigen, jar_eigen, alpha=0.2, s = 40)
    ax.scatter(unique_dfs_eigen, jar_eigen_median, color='r', s=70)
    ax.plot([-35, 35], [0, 0], c='black', ls='--')
    ax.plot([0, 0], [-15, 15], c='black', ls='--')
    ax.set_xlim([-35, 35])
    ax.set_ylim([-15, 15])
    ax.set_ylabel("response [Hz]", fontsize = fs)
    ax.set_xlabel("delta F [Hz]", fontsize = fs)
    #ax.set_title("JAR Eigenmannia virescens")

    #fig = plt.gcf()
    fig.savefig('../results/Vortrag/eigenmannia_medianJAR_df.png')


def plot_alle_apteronoti_JAR(jar_apti, df_apti, ):
    fig, ax = plt.subplots(1, 1, figsize=(x / inch, y / inch))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.96, top=0.9)

    unique_dfs_apti = np.unique(df_apti)
    jar_apti_median = []
    for udf in unique_dfs_apti:
        jar_apti_median.append(np.median(jar_apti[np.abs(df_apti - udf) < 2.5]))

    ax.scatter(df_apti, jar_apti, alpha=0.2, s=40)
    ax.scatter(unique_dfs_apti, jar_apti_median, color='r', s=70)
    ax.plot([-35, 35], [0, 0], c='black', ls='--')
    ax.plot([0, 0], [-15, 15], c='black', ls='--')
    ax.set_xlim([-35, 35])
    ax.set_ylim([-15, 15])
    ax.set_ylabel("response [Hz]", fontsize=fs)
    ax.set_xlabel("delta F [Hz]", fontsize=fs)
    #ax.set_title("JAR Apteronotus leptorhynchus", fontsize=fs)

    #fig = plt.gcf()
    fig.savefig('../results/Vortrag/apteronotus_medianJAR_df.png')

def plot_einzelne_Fische_JAR (id_alle, df):


    unique_ids = np.unique(id_alle)
    for ids in unique_ids:
        fig, ax = plt.subplots(1, 1, figsize=(x / inch, y / inch))
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.96, top=0.9)
        jar_alle = np.array(df.jar[df.id == ids])

        df_alle = np.array(df.df[df.id == ids])

        unique_dfs_alle = np.unique(df_alle)
        jar_alle_median = []
        for udf in unique_dfs_alle:
            jar_alle_median.append(np.median(jar_alle[np.abs(df_alle - udf) < 2.5]))
        ax.scatter(df_alle, jar_alle)
        ax.scatter(unique_dfs_alle, jar_alle_median, color='r')
        ax.plot([-35, 35], [0, 0], c='black', ls='--')
        ax.plot([0, 0], [-15, 15], c='black', ls='--')
        ax.set_xlim([-35, 35])
        ax.set_ylim([-15, 15])
        ax.set_ylabel("response [Hz]")
        ax.set_xlabel("delta F [Hz]")
        #ax.set_title(ids)
        fig.savefig('../results/Vortrag/' + ids + '_medianJAR_df.pdf')


            #fig = plt.gcf()


def plot_JAR_bodypara (unique_ids_eigen, df, specie):
    fig, ax = plt.subplots(1, 1, figsize=(x / inch, y / inch ))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.96, top=0.9)
    for ids in unique_ids_eigen:
        jar_eigen = np.array(df.jar[df.id == ids])

        df_eigen = np.array(df.df[df.id == ids])

        weight_eigen = np.unique(df.weight[df.id == ids])[0]
        size_eigen = np.unique(df['size'][df.id == ids])

        unique_dfs_eigen = np.unique(df_eigen)
        jar_eigen_median = []
        for udf in unique_dfs_eigen:
            jar_eigen_median.append(np.median(jar_eigen[np.abs(df_eigen - udf) < 2.5]))


        ax.plot(unique_dfs_eigen, jar_eigen_median, marker='', label='%.1fg, %.1fcm' % (weight_eigen, size_eigen))
    plt.legend(loc='lower left')
    ax.plot([-35, 35], [0, 0], c='black', ls='--')
    ax.plot([0, 0], [-8, 12], c='black', ls='--')
    ax.plot([0, 35], [0, 35], c='gray', ls='--')
    ax.set_xlim([-35, 35])
    ax.set_ylim([-8, 12])
    ax.set_ylabel("response [Hz]", fontsize = fs)
    ax.set_xlabel("delta F [Hz]", fontsize = fs)
    #ax.set_xticklabels(fontsize = fs)
    #ax.set_title('Korrelation zwischen JAR [Hz] und Gewicht [g]  ' +specie, fontsize = fs)
    return fig
    # fig = plt.gcf()





