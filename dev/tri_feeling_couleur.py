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

def selection(df, col, choice, lim, option):
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

        if option == "feeling":
            l_idx = [l_idx.rsplit("_", 1)[-1]]
        elif option == "color":
            l_idx = [l_idx.split("_")[-2]]

    else:
        l_idx = (cumsum[cumsum <= threshold].index).tolist()
        # print(cumsum_series[len(l_idx)])
        l_idx.append(cumsum.index[len(l_idx)])
        # On va chercher les éléments égaux à la dernière valeur qu'on a récupérée dans la liste pour les y ajouter (s'il y a égalité)
        last_value = res.loc[l_idx[-1], choice[0]]
        l_idx.extend(res[res[choice[0]] == last_value].index[len(res):])

        if option == "feeling":
            l_idx = [idx.rsplit("_", 1)[-1] for idx in l_idx]
        elif option == "color":
            l_idx = [idx.split("_")[-2] for idx in l_idx]

    return l_idx


#%%
####################################################################################################################################
# MAIN
####################################################################################################################################

def main():
    parent_path = pathlib.Path(__file__).parent.parent # Chemin parent du dossier (Emoskin)
    et = pd.read_excel(parent_path / "Files" / "ET_modified.xlsx", usecols="B:C, F:L, P:AO, AQ:AW, BC: BE", skiprows=6)


    feelings = ["Happy", "Relaxed", "Energized", "Surprised", "Self-Confident", "Sensual", "Reassured", "Calm", "Secured", "Intrigued", 
        "Hydrating", "Anti-Ageing", "Purifying", "Nourishing", "Soothing", "Refreshing", "Repairing", "Protecting", "Softening", "Glowing"]

    # We retrive the rows acquired after the chosing part
    et_p2d = et.loc[et.loc[:, "Parent Label"].str.contains("P2d", na=False), :]

    # Number of colors that were the most fixated for every emotion
    col_fix = "Fixation count"
    col_dur = "Duration of average fixation"
    col_ttff = "TTFF (AOI)"
    col_clicks = "Respondent count (mouse clicks)"

    maxi_fix = []
    maxi_dur = []
    maxi_ttff = []
    maxi_clicks = []

    for feeling in feelings:

        # Importation des données et calcul des moyennes et sommes (qui peuvent être des paramètres intéressants)
        fixations_df = et_p2d.loc[et_p2d.loc[:, "Parent Label"].str.contains(feeling), :]

        maxi_fix.append(selection(fixations_df, col_fix, ["sum", False], 0.3, "feeling"))
        maxi_dur.append(selection(fixations_df, col_dur, ["sum", False], 0.3, "feeling"))
        maxi_ttff.append(selection(fixations_df, col_ttff, ["mean", True], 0.1, "feeling"))
        maxi_clicks.append(selection(fixations_df, col_clicks, ["sum", False], 0.3, "feeling"))



    res_path = parent_path / "Results"
    res_path.mkdir(parents=True, exist_ok=True)


    maxi = pd.concat([pd.Series(maxi_fix, name="Color of the max of fixation count", index=feelings), 
        pd.Series(maxi_dur, name="Color of the max of avg duration of fixation", index=feelings), 
        pd.Series(maxi_ttff, name="Color of the min of TTFF", index=feelings),
        pd.Series(maxi_clicks, name="Color of the max of mouse clicks", index=feelings)], axis=1)


    file_name = "max_feelings.xlsx"
    maxi.to_excel(res_path / file_name)


    # On passe aux couleurs
    mask = et_p2d.loc[:, "Parent Label"].str.contains("|".join(feelings)).tolist()
    et_p2d = et_p2d[mask]

    colors = ["Whites", "Yellows", "Blues", "Greens", "Lavenders", "Oranges", "Reds"]


    # Création de listes qui vont contenirles résultats
    maxi_fix = []
    maxi_dur = []
    maxi_ttff = []
    maxi_clicks = []

    for color in colors:
        fixations_df = et_p2d.loc[et_p2d.loc[:, "Parent Label"].str.contains(color), :]

        maxi_fix.append(selection(fixations_df, col_fix, ["sum", False], 0.3, "color"))
        maxi_dur.append(selection(fixations_df, col_dur, ["sum", False], 0.3, "color"))
        maxi_ttff.append(selection(fixations_df, col_ttff, ["mean", True], 0.1, "color"))
        maxi_clicks.append(selection(fixations_df, col_clicks, ["sum", False], 0.3, "color"))

    maxi = pd.concat([pd.Series(maxi_fix, name="Emotion of the max of fixation count", index=colors), 
        pd.Series(maxi_dur, name="Emotion of the max of avg duration of fixation", index=colors), 
        pd.Series(maxi_ttff, name="Emotion of the max of TTFF", index=colors),
        pd.Series(maxi_clicks, name="Emotion of the max of mouse clicks", index=colors)], axis=1)


    file_name = "max_colors.xlsx"
    
    maxi.to_excel(res_path / file_name)




if __name__=="__main__":
    main()