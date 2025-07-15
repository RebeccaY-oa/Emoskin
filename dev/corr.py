#%%
####################################################################################################################################
# LIBRARIES
####################################################################################################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import pathlib
import seaborn as sns

#%%
####################################################################################################################################
# FUNCTIONS
####################################################################################################################################

#%%
####################################################################################################################################
# MAIN
####################################################################################################################################

def main():
    parent_path = pathlib.Path(__file__).parent.parent # Chemin parent du dossier (Emoskin)
    et = pd.read_excel(parent_path / "Files" / "ET.xlsx", usecols="B:C, G, I:K, O:AN, AP:AV, BB: BD", skiprows=6)
    # et = et.dropna(how = "any")

    # Calculer la matrice de corrélation
    matrice_correlation = et.corr()

    print(matrice_correlation)

    # matrice_correlation_kendall = df.corr(method='kendall')
    # print(matrice_correlation_kendall)

    # sns.heatmap(matrice_correlation, annot=True, cmap='coolwarm')
    # plt.show()
    # plt.savefig("heatmap.png")

    # sns.pairplot(et)
    # plt.show()
    # plt.savefig("pairplot.png")

    matrice_correlation.to_excel("correlation.xlsx")






if __name__=="__main__":
    main()