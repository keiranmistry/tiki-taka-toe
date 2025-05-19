import pandas as pd
import unicodedata
import re
from team_map import TEAM_NAME_MAP

def strip_accents(text):
    if isinstance(text, str):
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
    return text

# === Clean team name using map + fallback ===
def clean_team_name(team):
    team = strip_accents(team.strip())
    if team in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[team]
    # fallback: remove common suffixes and years
    team = re.sub(r'\b(?:FC|CF|SC|AC|AS|SS|US|UD|CD|AFC|[0-9]{4})\b', '', team, flags=re.IGNORECASE)
    team = re.sub(r'\s+', ' ', team).strip()
    return team

# === Load clubs.csv ===
df = pd.read_csv("clubs.csv")

# === Keep only clubs in top 5 European leagues ===
top_5_leagues = {"GB1", "ES1", "IT1", "FR1", "L1"}
df = df[df["id_current_league"].isin(top_5_leagues)]

# === Clean club_name using map ===
df["club_name"] = df["club_name"].apply(clean_team_name)

# === Drop duplicates if any club names are repeated ===
df = df.drop_duplicates(subset=["club_name"])

# === Save cleaned version ===
df.to_csv("cleaned_clubs.csv", index=False)
print("✅ Saved cleaned_clubs.csv")