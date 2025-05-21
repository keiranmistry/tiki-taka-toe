import pandas as pd
import random

df = pd.read_csv("cleaned_players.csv")

easy_clubs = [
    "Arsenal FC", "Chelsea FC", "Liverpool FC", "Manchester United",
    "Real Madrid", "FC Barcelona", "Juventus FC", "FC Bayern Munich",
    "Paris Saint-Germain", "AC Milan", "Inter Milan", "Borussia Dortmund"
]


easy_countries = [
    "England", "France", "Spain", "Germany", "Italy",
    "Portugal", "Argentina", "Brazil", "Netherlands"
]

# Now sample from these instead
clubs = random.sample(easy_clubs, 3)
countries = random.sample(easy_countries, 3)

# ✅ Display the selected grid
print("\n🎯 Soccer Tic Tac Toe Grid:\n")
print("            | " + " | ".join([c[:10].ljust(10) for c in countries]))
print("------------+" + "------------+" * 3)

for club in clubs:
    row = [club[:10].ljust(10)]
    for country in countries:
        row.append("   ___     ")
    print(" | ".join(row))

# Build a quick lookup: player name → list of (club, country)
from collections import defaultdict

# Build helper: name → list of team-country pairs
player_lookup = defaultdict(list)

for _, row in df.iterrows():
    name = row["name"]
    country = row["country"]
    team = row["team"]
    player_lookup[name].append((team, country))

# Create a set of all (club, country) pairs in the grid
grid_cells = [(club, country) for club in clubs for country in countries]

# Track guessed cells
guessed = {}

# Build player_dict again from CSV
player_dict = {}
for _, row in df.iterrows():
    pid = row["player_id"]
    if pid not in player_dict:
        player_dict[pid] = {
            "name": row["name"],
            "country": row["country"],
            "teams": set()
        }
    player_dict[pid]["teams"].add(row["team"])

# Make a map from name → list of player_ids (to handle duplicate names)
from collections import defaultdict
name_to_ids = defaultdict(list)
for pid, info in player_dict.items():
    name_to_ids[info["name"]].append(pid)

# Loop until all cells are guessed
while len(guessed) < 9:
    print("\n--- Grid ---")
    print("            | " + " | ".join([c[:10].ljust(10) for c in countries]))
    print("------------+" + "------------+" * 3)

    for club in clubs:
        row = [club[:10].ljust(10)]
        for country in countries:
            key = (club, country)
            if key in guessed:
                row.append(f" {guessed[key][:10]:<10}")
            else:
                row.append("   ___     ")
        print(" | ".join(row))

    print("\nEnter your guess for a cell:")
    club_guess = input("Club: ").strip()
    country_guess = input("Country: ").strip()
    player_guess = input("Player: ").strip()

    if (club_guess, country_guess) not in grid_cells:
        print("❌ That club-country combo is not in the grid. Try again.")
        continue

    valid = False
    for pid in name_to_ids.get(player_guess, []):
        info = player_dict[pid]
        if info["country"] == country_guess and club_guess in info["teams"]:
            guessed[(club_guess, country_guess)] = player_guess
            print("✅ Correct!")
            valid = True
            break

    if not valid:
        print("❌ Incorrect. Try again.")
