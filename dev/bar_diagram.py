import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
import pathlib
import natsort

parent_path = pathlib.Path(__file__).parent.parent

names = ["Happy_Yellows.xlsx", "Happy_Reds.xlsx", "Relaxed_Blues.xlsx", "Relaxed_Lavenders.xlsx", "Energized_Greens.xlsx", "Energized_Yellows.xlsx",
 "Surprised_Oranges.xlsx", "Surprised_Greens.xlsx", "Self-Confident_Reds.xlsx", "Self-Confident_Lavenders.xlsx", "Sensual_Reds.xlsx", 
 "Sensual_Lavenders.xlsx", "Reassured_Whites.xlsx", "Reassured_Blues.xlsx", "Reassured_Lavenders.xlsx", "Calm_Whites.xlsx", "Calm_Lavenders.xlsx",
 "Secured_Whites.xlsx", "Secured_Lavenders.xlsx", "Intrigued_Oranges.xlsx", "Intrigued_Lavenders.xlsx", "Hydrating_Blues.xlsx", 
 "Anti-Ageing_Whites.xlsx", "Anti-Ageing_Greens.xlsx", "Purifying_Whites.xlsx", "Purifying_Blues.xlsx", "Nourishing_Whites.xlsx", 
 "Nourishing_Greens.xlsx", "Soothing_Greens.xlsx", "Soothing_Blues.xlsx", "Refreshing_Blues.xlsx", "Refreshing_Greens.xlsx",
 "Repairing_Whites.xlsx", "Repairing_Greens.xlsx", "Protecting_Whites.xlsx", "Protecting_Lavenders.xlsx", "Softening_Reds.xlsx", 
 "Softening_Yellows.xlsx", "Glowing_Yellows.xlsx", "Glowing_Oranges.xlsx"]
criteres = ["Fixation count", "Duration of average fixation", "TTFF (AOI)", "Dwell time (fixation, ms)"]

hex = pd.read_excel(parent_path / "Files" / "code_hex.xlsx", sheet_name="Données Complètes palettes", index_col="Nom Teinte")

res_path = parent_path / "Results" / "Shades_by_emotion"

for name in names:
    name_split = re.split(r"[_.]", name)
    print(f"{name_split[0]}_{name_split[1]}")

    data = pd.read_excel(res_path / name, index_col="Label_modified")
    # data = data.sort_index(ascending=True)
    data = data.reindex(natsort.natsorted(data.index))
    hex_bis = hex[hex.index.isin(data.index)]
    hex_bis = hex_bis.reindex(data.index)
    colors = hex_bis["HEX"].tolist()
    
    for critere in criteres:
        res_path_bis = res_path / critere
        res_path_bis.mkdir(parents=True, exist_ok=True)
        fig, ax = plt.subplots()
        fig.set_figheight(9)
        fig.set_figwidth(18)      # fig.set_facecolor("#A6A6A6")
        ax.bar(data.index, data[critere], color=colors)
        ax.set_title(f"{critere} for {name_split[0]} {name_split[1]}", fontsize=24)
        ax.set_xlabel(f"{name_split[1]}", fontsize=16)
        ax.set_ylabel(f"{critere}", fontsize=16)
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontsize(14)
            label.set_fontstretch("ultra-condensed")
        # ax.set_facecolor("#A6A6A6")
        plt.tight_layout()
        plt.show()
        plt.savefig(res_path_bis / f"{name_split[0]}_{name_split[1]}.png")
        plt.close()