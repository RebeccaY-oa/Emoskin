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
def recup_infos_shades(colour, emotion, df, col_names):
    df = df.loc[df.loc[:, "Parent Label"].str.contains(f"{emotion}_{colour}", na=False)]
    df = df[["Label_modified"] + col_names]
    df["Label_modified"] = df["Label_modified"].str.split("_").str[-1] # Normalement, cette ligne permet de récupérer 
    df = df.set_index("Label_modified")
    df.to_excel(f"/home/user/Emoskin/Results/Shades_by_emotion/{emotion}_{colour}.xlsx")
    print(f"Le fichier {emotion}_{colour}.xlsx a bien été enregistré !")


#%%
####################################################################################################################################
# MAIN
####################################################################################################################################

def main():
    parent_path = pathlib.Path(__file__).parent.parent # Chemin parent du dossier (Emoskin)
    et = pd.read_excel(parent_path / "Files" / "ET_modified.xlsx", usecols="B:C, F:L, P:AO, AQ:AW, BC: BE", skiprows=6)

    dico = {
        "Happy": ["Yellows", "Reds"],
        "Relaxed" : ["Blues", "Lavenders"],
        "Energized": ["Yellows", "Greens"],
        "Surprised" : ["Oranges", "Greens"],
        "Self-Confident" : ["Reds", "Lavenders"],
        "Sensual" : ["Reds", "Lavenders"],
        "Reassured" : ["Whites", "Blues", "Lavenders"],
        "Calm" : ["Whites", "Lavenders"],
        "Secured" : ["Whites", "Lavenders"],
        "Intrigued" : ["Oranges", "Lavenders"],
        "Hydrating" : ["Blues"],
        "Anti-Ageing" : ["Whites", "Greens"],
        "Purifying" : ["Whites", "Blues"],
        "Nourishing" : ["Whites", "Greens"],
        "Soothing" : ["Greens", "Blues"],
        "Refreshing" : ["Blues", "Greens"],
        "Repairing" : ["Whites", "Greens"],
        "Protecting" : ["Whites", "Lavenders"],
        "Softening" : ["Reds", "Yellows"],
        "Glowing" : ["Yellows", "Oranges"]
    }

    # On récupère les lignes concernant P2d comme pour l'autre fichier
    et_p2d = et.loc[et.loc[:, "Parent Label"].str.contains("P2d", na=False), :]

    col_fix = "Fixation count"
    col_dur = "Duration of average fixation"
    col_ttff = "TTFF (AOI)"
    col_dt = "Dwell time (fixation, ms)"
    col_names = [col_fix, col_dur, col_ttff, col_dt]

    for feeling, colours in dico.items():
        for colour in colours:
            recup_infos_shades(colour, feeling, et_p2d, col_names)



if __name__=="__main__":
    main()