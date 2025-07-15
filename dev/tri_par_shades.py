#%%
####################################################################################################################################
# LIBRARIES
####################################################################################################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import pathlib


#%%
####################################################################################################################################
# FUNCTIONS
####################################################################################################################################
def selection(df, col, choice, lim):
    """
        Cette fonction a pour but de s'assurer que lorsqu'une couleur est majoritaire, elle est bien prise en compte et mise dans les indices.
        De plus, une couleur de plus est ajoutée à la liste: la couleur qui dépasse du seuil
    """
    res = df.groupby("Parent Label")[col].agg(["mean", "sum"])
    ord = res.sort_values(choice[0], ascending=choice[1])

    tot = ord[choice[0]].sum()
    cumsum = ord[choice[0]].cumsum()
    threshold = lim * tot

    if cumsum.iloc[0] > threshold:
        l_idx = cumsum.index[0]
        print(l_idx)
        l_idx = [l_idx.split("_")[-2]]

    else:
        l_idx = (cumsum[cumsum <= threshold].index).tolist()
        # print(cumsum_series[len(l_idx)])
        l_idx.append(cumsum.index[len(l_idx)])
        # On va chercher les éléments égaux à la dernière valeur qu'on a récupérée dans la liste pour les y ajouter (s'il y a égalité)
        last_value = res.loc[l_idx[-1], choice[0]]
        l_idx.extend(res[res[choice[0]] == last_value].index[len(res):])
        
        l_idx = [idx.split("_")[-2] for idx in l_idx]

    return l_idx


#%%
####################################################################################################################################
# MAIN
####################################################################################################################################
def main():
    parent_path = pathlib.Path(__file__).parent.parent # Chemin parent du dossier (Emoskin)
    et = pd.read_excel(parent_path / "Files" / "ET_modified.xlsx", usecols="B:C, F:L, P:AO, AQ:AW, BC: BE", skiprows=6)

    # Je souhaite cette fois-ci regarder quelles sont les émotions prédominentes en fonction des couleurs
    # Ca va être assez similaire à l'autre code (en quelcuqe sorte tourné dans un autre sens quoi)
    feelings = ["Happy", "Relaxed", "Energized", "Surprised", "Self-Confident", "Sensual", "Reassured", "Calm", "Secured", "Intrigued", 
        "Hydrating", "Anti-Ageing", "Purifying", "Nourishing", "Soothing", "Refreshing", "Repairing", "Protecting", "Softening", "Glowing"]
    colors = ["Whites", "Yellows", "Blues", "Greens", "Lavenders", "Oranges", "Reds"]

    # On récupère les lignes concernant P2d comme pour l'autre fichier
    et_p2d = et.loc[et.loc[:, "Parent Label"].str.contains("P2d", na=False), :]

    # On récupère toutes les métriques que l'on souhaite étudier
    col_fix = "Fixation count"
    col_dur = "Duration of average fixation"
    col_ttff = "TTFF (AOI)"
    col_clicks_resp = "Respondent count (mouse clicks)"
    col_clicks = "Mouse click count"
    mask = et_p2d.loc[:, "Parent Label"].str.contains("|".join(feelings)).tolist()
    et_p2d = et_p2d[mask]

    # shades = fixations_df.loc[:, "Label"]  # List of all the possible shades but may be useless

    fixations_df_by_shade = et_p2d.groupby("Label_modified") # Normalement on regroupe tout par shades et donc il doit y avoir 20 lignes,
    # chacune étant associée à une émotion en particulier
    # Je vais d'abord agglomérer les résultats pour avoir le nb de fixations, de durée de fixation, TTFF et clicks par shade

    # metrics_by_shade = fixations_df_by_shade[[col_fix, col_dur, col_ttff, col_clicks]].agg(["sum", "mean"])
    metrics_by_shade = fixations_df_by_shade.agg(
        fix_sum=(col_fix, "sum"),
        fix_mean=(col_fix, "mean"),
        dur_sum=(col_dur, "sum"),
        dur_mean=(col_dur, "mean"),
        ttff_sum=(col_ttff, "sum"),
        ttff_mean=(col_ttff, "mean"),
        clicks_resp_sum=(col_clicks_resp, "sum"),
        clicks_resp_mean=(col_clicks_resp, "mean"),
        clicks_sum=(col_clicks, "sum"),
        clicks_mean=(col_clicks, "mean")
    )

    metrics_by_shade = metrics_by_shade.rename(
        columns={
            "fix_sum" : f"Somme de {col_fix}", "fix_mean" : f"Moyenne de {col_fix}", "dur_sum" : f"Somme de {col_dur}", 
            "dur_mean" : f"Moyenne de {col_dur}", "ttff_sum" : f"Somme de {col_ttff}", "ttff_mean" : f"Moyenne de {col_ttff}",
            "clicks_resp_sum" : f"Somme de {col_clicks_resp}", "clicks_resp_mean" : f"Moyenne de {col_clicks_resp}", 
            "clicks_sum" : f"Somme de {col_clicks}", "clicks_mean" : f"Moyenne de {col_clicks}"
            }
    )

    # On enlève les P2d qui sont devant les noms
    metrics_by_shade.index = metrics_by_shade.index.str.split("_").str[-1]

    # Récupérer le fichier excel des surveys, calculer le nombre de clic pour chacune des shades et faire une jointure avec le tableau des 
    # résultats par shade

    survey = pd.read_excel(parent_path / "Files" / "survey.xlsx",sheet_name="Full Survey Response", usecols="M")
    nb_clicks = survey.value_counts()

    # nb_clicks.rename("Real Clicks Count")

    nb_clicks.index = nb_clicks.index.get_level_values(0)

    print(nb_clicks)
    # nb_clicks.reset_index(inplace=True)

    print(nb_clicks)

    metrics_by_shade = metrics_by_shade.join(nb_clicks)

    res_path = parent_path / "Results"
    res_path.mkdir(parents=True, exist_ok=True)


    file_name = "fixations_by_shade.xlsx"


    # with open(res_path / file_name, "w") as my_file:
    #     my_file.write(f"{maxi}\n\n")
    
    metrics_by_shade.to_excel(res_path / file_name)

    # metrics_by_shade.sort_values("Real Clicks Count", ascending=True)
    metrics_by_shade.sort_values("count", ascending=True)

    plt.figure()
    plt.bar(metrics_by_shade.index, metrics_by_shade["Moyenne de Fixation count"].values)
    plt.xlabel("Couleurs")
    plt.ylabel("Nombre moyen de fixations")
    plt.legend()
    plt.show()
    plt.savefig(res_path / "graphique.png")







if __name__ == "__main__":
    main()