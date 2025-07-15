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


#%%
####################################################################################################################################
# MAIN
####################################################################################################################################
def main():
    parent_path = pathlib.Path(__file__).parent.parent # Chemin parent du dossier (Emoskin)
    emotions = pd.read_excel("/home/user/Emoskin/Files/emotion_survey.xlsx", sheet_name="Emotion Survey Response") # On récupère les résultats
    functional_benefits = pd.read_excel("/home/user/Emoskin/Files/functional_benefits.xlsx", sheet_name="Benefits survey")

    feelings = ["Happy", "Relaxed", "Energized", "Surprised", "Self-Confident", "Sensual", "Reassured", "Calm", "Secured", "Intrigued", 
        "Hydrating", "Anti-Ageing", "Purifying", "Nourishing", "Soothing", "Refreshing", "Repairing", "Protecting", "Softening", "Glowing"]
    
    # On calcule quelle est la couleur la plus cliquée pour chaque émotion et on l'écrit dans un txt
    best_shade_by_emotion = {}
    
    for emotion in feelings[:10]:
        int_df = emotions[emotions["Emotion"] == emotion]
        int_df = int_df.set_index("OA_Name")
        best_shade_by_emotion[emotion] = int_df["Nb OA_clics"].idxmax() # Indice du maximum


    with open("/home/user/Emoskin/Results/max_shade_by_emotion.txt", "w") as my_file:
        for emotion, shade in best_shade_by_emotion.items():
            my_file.write(f"La teinte la plus cliquée pour l'émotion {emotion} est {shade}.\n\n")


    # On calcule quelle est la couleur la plus cliquée pour chaque bénéfice fonctionnel et on l'écrit dans un txt
    best_shade_by_benefit = {}
    
    for benefit in feelings[10:]:
        int_df = functional_benefits[functional_benefits["Benefit"] == benefit]
        int_df = int_df.set_index("OA_Name")
        best_shade_by_benefit[benefit] = int_df["Nb OA_clics"].idxmax() # Indice du maximum


    with open("/home/user/Emoskin/Results/max_shade_by_benefit.txt", "w") as my_file:
        for benefit, shade in best_shade_by_benefit.items():
            my_file.write(f"La teinte la plus cliquée pour l'émotion {benefit} est {shade}.\n\n")



    # On analyse les résultats des respondents pour savoir s'ils ont un pattern de couleurs à choisir
    informations = pd.read_excel("/home/user/Emoskin/Files/emotion_survey.xlsx", sheet_name="Full Survey Response")
    # info_by_respondent = informations.groupby(["Respondent ID", "Choice"]).size()
    # info_by_respondent = informations.groupby(["Respondent ID", "Choice"])[["Word_EmotionOrBenefit"]].apply(lambda x: x)
    info_by_respondent = informations.groupby(["Respondent ID", "Choice"])['Word_EmotionOrBenefit'].agg(list)
    # info_by_respondent = informations.set_index(["Respondent ID", "Choice"])
    # info_by_respondent = info_by_respondent.sort_index()
    # Je souhaite avoir le ratio de chaque couleur que les respondents ont choisi. Ex: whites: 17%, and so on
    choice_counts = informations.groupby("Respondent ID")["Choice"].value_counts().rename("Choice count")

    # info_by_respondent = info_by_respondent.merge(choice_counts, left_index=True, right_index=True, how="left")

    info_by_respondent = pd.concat([info_by_respondent, choice_counts], axis=1)



    # print(info_by_respondent)
    info_by_respondent.to_excel("/home/user/Emoskin/Results/Categories_de_couleur_par_respondent.xlsx")


if __name__ == "__main__":
    main()