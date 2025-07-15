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

def selection(df, col, type):
    """
        Cette fonction a pour but de s'assurer que lorsqu'une couleur est majoritaire, elle est bien prise en compte et mise dans les indices.
        De plus, une couleur de plus est ajoutée à la liste: la couleur qui dépasse du seuil
    """
    if type == "feeling":
        name =  "Colour"
        res = df[["Label", col]]
        if col == "Fixation count":
            res[f"% {col}"] = res[col]/res[col].sum()
        res = res.rename(columns = {"Label": name})
        res[name] = res[name].str.split("_").str[-1]

    
    elif type == "color":
        name = "Feeling"
        res = df[["Parent Label", col]]
        if col == "Fixation count":
            res[f"% {col}"] = res[col]/res[col].sum()
        res = res.rename(columns = {"Parent Label": name})
        res[name] = res[name].str.split("_").str[-1]

    return res, name



#%%
####################################################################################################################################
# MAIN
####################################################################################################################################

def main():
    parent_path = pathlib.Path(__file__).parent.parent # Chemin parent du dossier (Emoskin)
    et = pd.read_excel(parent_path / "Files" / "ET_modified.xlsx", usecols="B:C, F:L, P:AO, AQ:AW, BC: BE", skiprows=6)
    emotion = pd.read_excel(parent_path / "Files" / "emotion_survey.xlsx", sheet_name="Emotion Survey Response")
    functional_benefits = pd.read_excel(parent_path / "Files" / "functional_benefits.xlsx", sheet_name="Benefits survey")


    feelings = ["Happy", "Relaxed", "Energized", "Surprised", "Self-Confident", "Sensual", "Reassured", "Calm", "Secured", "Intrigued", 
        "Hydrating", "Anti-Ageing", "Purifying", "Nourishing", "Soothing", "Refreshing", "Repairing", "Protecting", "Softening", "Glowing"]
    
    colors = ["Whites", "Yellows", "Blues", "Greens", "Lavenders", "Oranges", "Reds"]

    # We retrive the rows acquired after the chosing part
    et_p2b = et.loc[et.loc[:, "Parent Label"].str.contains("P2b", na=False), :]

    # et_p2b.to_excel(parent_path / "et_p2b.xlsx")

    # Number of colors that were the most fixated for every emotion
    col_resp = "Respondent count (fixation dwells)"
    col_ratio = "Respondent ratio (fixation dwells)"
    col_fix = "Fixation count"
    col_dur = "Duration of average fixation"
    col_ttff = "TTFF (AOI)"
    col_dt = "Dwell time (fixation, ms)"
    col_dt_ratio = "Dwell time (fixation, %)"
    # col_clicks = "Respondent count (mouse clicks)"
    col = [col_resp, col_ratio, col_fix, col_dur, col_ttff, col_dt, col_dt_ratio]

    list_colors = "|".join(colors)
    list_res = []

    res_path = parent_path / "Results" / "Tableaux" / "Feelings"
    res_path.mkdir(parents=True, exist_ok=True)
    
    i = 0
    for feeling in feelings:
        # Importation des données et calcul des moyennes et sommes (qui peuvent être des paramètres intéressants)
        fixations_df = et_p2b.loc[(et_p2b.loc[:, "Parent Label"].str.contains(feeling)) & 
                                  (~et_p2b.loc[:, "Parent Label"].str.contains(list_colors)), :] # Sélectionne les éléments qui contiennent un
        # bénéfice fonctionnel ou une émotion sans correspondre à une couleur spécifique
        res_resp, _ = selection(fixations_df, col_resp, "feeling")
        res_ratio, _ = selection(fixations_df, col_ratio, "feeling")
        res_fix, _ = selection(fixations_df, col_fix, "feeling")
        res_dur, _ = selection(fixations_df, col_dur, "feeling")
        res_ttff, _ = selection(fixations_df, col_ttff, "feeling")
        res_dt, _ = selection(fixations_df, col_dt, "feeling")
        res_dt_ratio, name = selection(fixations_df, col_dt_ratio, "feeling")
        res_resp = res_resp.set_index(name)
        res_ratio = res_ratio.set_index(name)
        res_fix = res_fix.set_index(name)
        res_dur = res_dur.set_index(name)
        res_ttff = res_ttff.set_index(name)
        res_dt = res_dt.set_index(name)
        res_dt_ratio = res_dt_ratio.set_index(name)
        # res_col = []

        res = pd.concat([res_resp, res_ratio, res_fix, res_dur, res_ttff, res_dt, res_dt_ratio], axis=1, sort=False)
        res["Feeling"] = feeling
        if i < 10:
            nb_clics = emotion.loc[emotion.loc[:, "Emotion"] == feeling].groupby("Nb OA_clics")[["Nb OA_clics"]].count()
        else:
            nb_clics = functional_benefits.loc[functional_benefits.loc[:, "Benefit"] == feeling].groupby("Nb OA_clics")[["Nb OA_clics"]].count()
        res = res.join(nb_clics, how="left")
        res = res.set_index(["Feeling", res.index])
        list_res.append(res)
        i += 1
    df_res = pd.concat(list_res, axis=0)
    df_res.to_excel(res_path / "Feelings.xlsx")


    # # On passe aux couleurs par rapport aux émotions
    list_colors = "|".join(colors + ["ChoiceLoop"])
    list_feelings = "|".join(feelings[:10])
    list_res = []
    res_col = []
    # print(list_feelings)

    res_path = parent_path / "Results" / "Tableaux" / "Colors" / "Emotions"
    res_path.mkdir(parents=True, exist_ok=True)

    for color in colors:
        # Importation des données et calcul des moyennes et sommes (qui peuvent être des paramètres intéressants)
        fixations_df = et_p2b.loc[(et_p2b.loc[:, "Label"].str.contains(color)) & 
                                  (~et_p2b.loc[:, "Parent Label"].str.contains(list_colors)) &
                                  (et_p2b.loc[:, "Parent Label"].str.contains(list_feelings)), :] # Sélectionne les éléments qui contiennent un
        # bénéfice fonctionnel ou une émotion sans correspondre à une couleur spécifique
        res_resp, _ = selection(fixations_df, col_resp, "color")
        res_ratio, _ = selection(fixations_df, col_ratio, "color")
        res_fix, _ = selection(fixations_df, col_fix, "color")
        res_dur, _ = selection(fixations_df, col_dur, "color")
        res_ttff, _ = selection(fixations_df, col_ttff, "color")
        res_dt, _ = selection(fixations_df, col_dt, "color")
        res_dt_ratio, name = selection(fixations_df, col_dt_ratio, "color")
        res_resp = res_resp.set_index(name)
        res_ratio = res_ratio.set_index(name)
        res_fix = res_fix.set_index(name)
        res_dur = res_dur.set_index(name)
        res_ttff = res_ttff.set_index(name)
        res_dt = res_dt.set_index(name)
        res_dt_ratio = res_dt_ratio.set_index(name)
        # res_col = []

        res = pd.concat([res_resp, res_ratio, res_fix, res_dur, res_ttff, res_dt, res_dt_ratio], axis=1, sort=False)
        res["Colour"] = color
        nb_clics = emotion.loc[emotion.loc[:, "Choice"] == color].groupby("Emotion")[["Emotion"]].count()
        res = res.join(nb_clics, how="left")
        res = res.set_index(["Colour", res.index])
        list_res.append(res)

    df_res = pd.concat(list_res, axis=0)
    df_res.to_excel(res_path / "Emotions.xlsx")

    
    # # On passe aux couleurs par rapport aux bénéfices fonctionnels
    list_colors = "|".join(colors + ["ChoiceLoop"])
    list_functional_benefits = "|".join(feelings[10:])
    list_res = []

    res_path = parent_path / "Results" / "Tableaux" / "Colors" / "Functional Benefits"
    res_path.mkdir(parents=True, exist_ok=True)

    for color in colors:
        # Importation des données et calcul des moyennes et sommes (qui peuvent être des paramètres intéressants)
        fixations_df = et_p2b.loc[(et_p2b.loc[:, "Label"].str.contains(color)) & 
                                  (~et_p2b.loc[:, "Parent Label"].str.contains(list_colors)) &
                                  (et_p2b.loc[:, "Parent Label"].str.contains(list_functional_benefits)), :] 
        # Sélectionne les éléments qui contiennent un
        # bénéfice fonctionnel ou une émotion sans correspondre à une couleur spécifique
        res_resp, _ = selection(fixations_df, col_resp, "color")
        res_ratio, _ = selection(fixations_df, col_ratio, "color")
        res_fix, _ = selection(fixations_df, col_fix, "color")
        res_dur, _ = selection(fixations_df, col_dur, "color")
        res_ttff, _ = selection(fixations_df, col_ttff, "color")
        res_dt, _ = selection(fixations_df, col_dt, "color")
        res_dt_ratio, name = selection(fixations_df, col_dt_ratio, "color")
        res_resp = res_resp.set_index(name)
        res_ratio = res_ratio.set_index(name)
        res_fix = res_fix.set_index(name)
        res_dur = res_dur.set_index(name)
        res_ttff = res_ttff.set_index(name)
        res_dt = res_dt.set_index(name)
        res_dt_ratio = res_dt_ratio.set_index(name)
        # res_col = []

        res = pd.concat([res_resp, res_ratio, res_fix, res_dur, res_ttff, res_dt, res_dt_ratio], axis=1, sort=False)
        res["Colour"] = color
        nb_clics = functional_benefits.loc[functional_benefits.loc[:, "Choice"] == color].groupby("Benefit")[["Benefit"]].count()
        res = res.join(nb_clics, how="left")
        res = res.set_index(["Colour", res.index])
        list_res.append(res)

    df_res = pd.concat(list_res, axis=0)
    df_res.to_excel(res_path / "Functional_Benefits.xlsx")



if __name__=="__main__":
    main()