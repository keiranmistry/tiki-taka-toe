import pandas as pd
import random
from valid_pairs import VALID_PAIRS

df = pd.read_csv("cleaned_players.csv")

easy_clubs = [
    "Arsenal", "Chelsea", "Tottenham", "Man United",
    "Man City", "Liverpool", "PSG", "Barcelona", "Real Madrid",
    "Atletico Madrid", "Bayern Munich", "Borussia Dortmund",
    "Juventus", "Milan", "Inter"
]

medium_clubs = easy_clubs + [
    "Monaco", "Roma", "Atalanta", "Aston Villa", "Bayer Leverkusen", 
    "Everton", "Newcastle", "Marseille", "Leipzig", "Real Sociedad",
    "Napoli", "Sevilla", "Brighton", "West Ham"
]

hard_clubs = medium_clubs + ['Angers', 'Athletic Bilbao', 'Augsburg', 
    'Auxerre', 'Bochum', 'Bologna', 'Borussia Monchengladbach', 
    'Bournemouth', 'Brentford', 'Brest', 'Cagliari', 'Celta Vigo', 
    'Como', 'Crystal Palace', 'Deportivo', 'Empoli', 'Espanyol', 
    'Fiorentina', 'Frankfurt', 'Freiburg', 'Fulham', 'Genoa', 'Getafe', 
    'Girona', 'Heidenheim', 'Hoffenheim', 'Holstein Kiel', 'Ipswich', 
    'Las Palmas', 'Lazio', 'Le Havre', 'Lecce', 'Leganes', 'Leicester', 
    'Lens', 'Lille', 'Lyon', 'Mainz', 'Mallorca', 'Montpellier', 'Monza', 
    'Nantes', 'Nice', 'Nottingham Forest', 'Osasuna', 'Parma', 'Rayo Vallecano', 
    'Real Betis', 'Real Valladolid', 'Reims', 'Rennes', 'Saint-Etienne', 
    'Southampton', 'St Pauli', 'Strasbourg', 'Stuttgart', 'Torino', 'Toulouse',
    'Udinese', 'Union Berlin', 'Valencia', 'Venezia', 'Verona', 'Villarreal', 
    'Werder Bremen', 'Wolfsburg', 'Wolves'
]


easy_countries = [
    "England", "France", "Spain", "Germany", "Italy",
    "Portugal", "Argentina", "Brazil", "Netherlands"
]


print("Choose difficulty\n" \
    "1: Easy\n2: Medium\n3: Hard")
choice = input()
choice = int(choice)
while choice != 1 and choice != 2 and choice != 3:
    print("Enter valid input.")
    choice = input()
    choice = int(choice)
if choice == 1:
    difficulty = easy_clubs
elif choice == 2:
    difficulty = medium_clubs
else:
    difficulty = hard_clubs
    
# Build sets of valid countries and clubs based on VALID_PAIRS
valid_pairs = set(VALID_PAIRS.keys())
valid_countries = set([country for (country, _) in valid_pairs])
valid_clubs = set([club for (_, club) in valid_pairs])

# Filter your desired pools to ensure they're valid
filtered_clubs = [club for club in difficulty if club in valid_clubs]
filtered_countries = [country for country in easy_countries if country in valid_countries]

# Keep picking until we find a valid 3x3 grid
while True:
    clubs = random.sample(filtered_clubs, 3)
    countries = random.sample(filtered_countries, 3)

    # Ensure all (country, club) pairs exist in VALID_PAIRS
    if all((country, club) in valid_pairs for club in clubs for country in countries):
        break

# ✅ Display the selected grid
print("\n🎯 Soccer Tic Tac Toe Grid:\n")
print("            | " + " | ".join([c[:10].ljust(10) for c in countries]))
print("------------+" + "------------+" * 3)

for club in clubs:
    row = [club[:10].ljust(10)]
    for country in countries:
        row.append("   ___     ")
    print(" | ".join(row))

# Save valid cell positions
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

    key = (country_guess, club_guess)
    valid_names = VALID_PAIRS.get(key, [])

    # Normalize user guess
    guess = player_guess.strip().lower()

    # Step 1: Check full name match
    for name in valid_names:
        if guess == name.lower():
            guessed[(club_guess, country_guess)] = name
            print("✅ Correct! (full name match)")
            break
    else:
        # Step 2: Check partial match (everything except the first word)
        matched = False
        for name in valid_names:
            parts = name.split()
            if len(parts) == 1:
                partial = parts[0].lower()
            else:
                partial = " ".join(parts[1:]).lower()
            if guess == partial:
                guessed[(club_guess, country_guess)] = name
                print(f"✅ Correct! (matched partial: {name})")
                matched = True
                break

        if not matched:
            print("❌ Incorrect. Try again.")

