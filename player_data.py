import pandas as pd
from collections import defaultdict
import unicodedata
from team_map import TEAM_NAME_MAP


# Helper function to remove accents
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
    return team

# === LOAD CSV FILES ===
transfers = pd.read_csv("transfers.csv")
players = pd.read_csv("players.csv")
clubs = pd.read_csv("clubs.csv")

# === RENAME COLUMNS FOR MERGING ===
players = players.rename(columns={"id": "player_id"})
clubs = clubs.rename(columns={"id": "club_id"})

# === MERGE PLAYER INFO INTO TRANSFERS ===
merged = transfers.merge(players[['player_id', 'name', 'citizenship_1']], on="player_id", how="left")

# === MERGE JOINED CLUB INFO ===
merged = merged.merge(clubs[['club_id', 'club_name', 'id_current_league']], 
                      left_on="joined_club_id", 
                      right_on="club_id", 
                      how="left")

# === RENAME AND CLEAN ===
merged = merged.rename(columns={"club_name": "joined_club", "id_current_league": "league"})
merged = merged.drop(columns=["club_id"])
merged = merged.dropna(subset=["name", "citizenship_1", "joined_club", "league"])

# === FILTER FOR MAJOR LEAGUES ===
target_leagues = {"IT1", "GB1", "ES1", "L1", "FR1"}
merged = merged[merged["league"].isin(target_leagues)]
print("Number of rows after filtering:", len(merged))
print("Sample rows after filtering:")
print(merged[['player_id', 'name', 'citizenship_1', 'joined_club']].head())

# === BUILD PLAYER DICTIONARY ===
player_dict = {}
name_to_ids = defaultdict(list)

for _, row in merged.iterrows():
    player_id = row['player_id']
    name = strip_accents(row['name'])
    country = strip_accents(row['citizenship_1'])
    joined = clean_team_name(row['joined_club'])


    if player_id not in player_dict:
        player_dict[player_id] = {
            "name": name,
            "country": country,
            "teams": set()
        }
    player_dict[player_id]["teams"].add(joined)


# === Convert player_dict to flat rows for CSV ===
rows = []

for pid, info in player_dict.items():
    for team in info["teams"]:
        rows.append({
            "player_id": pid,
            "name": strip_accents(info["name"]),
            "country": strip_accents(info["country"]),
            "team": strip_accents(team)
        })


# === Save to cleaned_players.csv ===
import os
df_out = pd.DataFrame(rows)
df_out.to_csv("cleaned_players.csv", index=False)

print("✅ Saved cleaned_players.csv at:")
print(os.path.abspath("cleaned_players.csv"))
df = pd.read_csv("cleaned_players.csv")



