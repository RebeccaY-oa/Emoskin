import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Création d'un DataFrame exemple avec des données corrélées
np.random.seed(0)
n_samples = 100
x1 = np.random.rand(n_samples)
x2 = 2 * x1 + np.random.rand(n_samples) * 0.1 # x2 est fortement corrélée à x1
x3 = 0.5 * x1 - 3 * np.random.rand(n_samples) * 0.1 # x3 est corrélée à x1
df = pd.DataFrame({'x1': x1, 'x2': x2, 'x3': x3})


# 1. Standardisation des données (important pour la PCA)
# La PCA est sensible aux échelles des variables.  Il est donc important de standardiser 
# les données avant d'appliquer la PCA, surtout si les variables ont des unités différentes.

scaler = StandardScaler()
scaled_data = scaler.fit_transform(df)


# 2. Application de la PCA
pca = PCA(n_components=2) # On choisit de réduire à 2 composantes principales
principal_components = pca.fit_transform(scaled_data)

# Créer un nouveau DataFrame avec les composantes principales
df_pca = pd.DataFrame(data = principal_components, columns = ['composante_principale_1', 'composante_principale_2'])

df_pca.to_excel("pca.xlsx")
# 3. Visualisation des composantes principales

plt.scatter(df_pca['composante_principale_1'], df_pca['composante_principale_2'])
plt.xlabel('Composante Principale 1')
plt.ylabel('Composante Principale 2')
plt.title('Visualisation des données après PCA')
plt.show()

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
df_composantes = pd.DataFrame(pca.components_, columns=df.columns, index = ['CP1','CP2'])
print("\nDataFrame des composantes :\n", df_composantes)


# Visualiser les composantes
df_composantes.plot(kind='bar')
plt.title('Poids des variables dans les composantes principales')
plt.xlabel('Composantes principales')
plt.ylabel('Poids')
plt.show()
plt.savefig("coucou.png")