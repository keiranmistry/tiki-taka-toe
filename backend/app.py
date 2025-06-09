from flask import Flask, request, jsonify
import pandas as pd
import random
from backend.valid_pairs import VALID_PAIRS

app = Flask(__name__)
df = pd.read_csv("data/cleaned_players.csv")

# Helper: get a valid grid
def generate_grid(clubs, countries):
    valid_pairs = set(VALID_PAIRS.keys())
    valid_clubs = [club for club in clubs if any((c, club) in valid_pairs for c in countries)]
    valid_countries = [c for c in countries if any((c, club) in valid_pairs for club in clubs)]

    while True:
        selected_clubs = random.sample(valid_clubs, 3)
        selected_countries = random.sample(valid_countries, 3)
        if all((c, club) in valid_pairs for club in selected_clubs for c in selected_countries):
            return selected_clubs, selected_countries

@app.route("/generate-grid")
def generate_grid_endpoint():
    clubs = request.args.get("difficulty", "easy")
    if clubs == "medium":
        from backend.difficulty import medium_clubs as club_pool
    elif clubs == "hard":
        from backend.difficulty import hard_clubs as club_pool
    else:
        from backend.difficulty import easy_clubs as club_pool

    countries = ["England", "France", "Spain", "Germany", "Italy",
                 "Portugal", "Argentina", "Brazil", "Netherlands"]

    grid_clubs, grid_countries = generate_grid(club_pool, countries)
    return jsonify({
        "clubs": grid_clubs,
        "countries": grid_countries
    })

@app.route("/submit-guess", methods=["POST"])
def submit_guess():
    data = request.get_json()
    club = data["club"]
    country = data["country"]
    player_input = data["player"]

    guesses = df[(df["team"] == club) & (df["country"] == country)]
    for _, row in guesses.iterrows():
        full_name = row["name"]
        parts = full_name.strip().split()
        alt_name = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
        if player_input.lower() in (full_name.lower(), alt_name.lower()):
            return jsonify({"result": "correct", "player": full_name})

    return jsonify({"result": "incorrect"})

if __name__ == "__main__":
    app.run(debug=True)
