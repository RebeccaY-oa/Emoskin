#%%
####################################################################################################################################
# LIBRARIES
####################################################################################################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import pathlib
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

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
    et = et.dropna(how = "any")

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(et)

    # Méthode du coude pour choisir le bon nombre de composantes principales
    # pca = PCA()  # Créer un objet PCA sans spécifier le nombre de composantes
    # pca.fit(scaled_data)

    # # Variance expliquée par chaque composante
    # variance_expliquee = pca.explained_variance_ratio_

    # # Variance expliquée cumulée
    # variance_expliquee_cumulee = np.cumsum(variance_expliquee)

    # # Tracer la variance expliquée cumulée
    # plt.plot(range(1, len(variance_expliquee_cumulee) + 1), variance_expliquee_cumulee)
    # plt.xlabel("Nombre de composantes principales")
    # plt.ylabel("Variance expliquée cumulée")
    # plt.title("Variance expliquée cumulée en fonction du nombre de composantes")
    # plt.grid(True)
    # plt.show()

    # plt.savefig("coucou.png")

    pca = PCA(n_components=10)

    principal_components = pca.fit_transform(scaled_data)

    # Créer un nouveau DataFrame avec les composantes principales
    df_pca = pd.DataFrame(data = principal_components, columns = [f'composante_principale_{i+1}' for i in range(10)])


    # 4. Variance expliquée par chaque composante principale
    print("Variance expliquée par chaque composante : ", pca.explained_variance_ratio_)
    # Plus la variance expliquée par les premières composantes est élevée, plus la 
    # réduction de dimension est efficace.



    # 5. Composantes de la PCA
    print("\nComposantes de la PCA :\n", pca.components_)
    # Les composantes de la PCA indiquent les poids de chaque variable originale dans
    # la construction des composantes principales.  On peut observer que x1 et x2 ont
    # des poids importants dans la première composante principale, ce qui confirme leur
    # forte corrélation.

    # Afficher les composantes sous forme de DataFrame pour plus de clarté
    df_composantes = pd.DataFrame(pca.components_, columns=et.columns, index = [f'CP{i+1}' for i in range(10)])
    print("\nDataFrame des composantes :\n", df_composantes)

    df_composantes.to_excel("pca.xlsx")


    # Visualiser les composantes
    df_composantes.plot(kind='bar')
    plt.title('Poids des variables dans les composantes principales')
    plt.xlabel('Composantes principales')
    plt.ylabel('Poids')
    plt.show()
    plt.savefig("poids.png")




if __name__=="__main__":
    main()