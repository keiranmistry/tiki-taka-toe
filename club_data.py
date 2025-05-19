import pandas as pd
import unicodedata
import re
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
    if team in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[team]
    team = re.sub(r'\b(?:FC|CF|SC|AC|AS|SS|US|UD|CD|AFC|[0-9]{4})\b', '', team, flags=re.IGNORECASE)
    team = re.sub(r'\s+', ' ', team).strip()
    return team

# === Load and clean ===
df = pd.read_csv("clubs.csv")
top_5_leagues = {"GB1", "ES1", "IT1", "FR1", "L1"}
df = df[df["id_current_league"].isin(top_5_leagues)]
df["club_name"] = df["club_name"].apply(clean_team_name)
df = df.drop_duplicates(subset=["club_name"])

# ✅ Ensure 'url' is a string so pandas quotes it
df["url"] = df["url"].astype(str)

# ✅ Quote only string fields — so url will be quoted, numbers will not
df.to_csv("cleaned_clubs.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
print("✅ Saved cleaned_clubs.csv")
