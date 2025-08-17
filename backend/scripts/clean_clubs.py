import pandas as pd
import unicodedata
import csv
from team_map import TEAM_NAME_MAP

def strip_accents(text):
    if isinstance(text, str):
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
    return text

def clean_team_name(team):
    team = strip_accents(team.strip())
    return TEAM_NAME_MAP[team]


df = pd.read_csv("clubs.csv")

'''
GB1: Premier League
ES1: La Liga
IT1: Serie A
FR1: Ligue 1
L1: Bundesliga
'''

top_5_leagues = {"GB1", "ES1", "IT1", "FR1", "L1"}

#Edit dataframe
df = df[df["id_current_league"].isin(top_5_leagues)]
df["club_name"] = df["club_name"].apply(clean_team_name)
df = df.drop_duplicates(subset=["club_name"])


df["url"] = df["url"].astype(str)

df.to_csv("cleaned_clubs.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
print("Saved cleaned_clubs.csv")
