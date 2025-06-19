from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import random
import os
from valid_pairs import VALID_PAIRS
from difficulty import easy_clubs, medium_clubs, hard_clubs

import requests
from flask import send_file
from io import BytesIO

# Define app first
app = Flask(__name__)

# THEN enable CORS
CORS(app)

# Now continue with your code...

# === Load cleaned player data ===
DATA_PATH = os.path.join("data", "cleaned_players.csv")
df = pd.read_csv(DATA_PATH)

# === Root health check ===
@app.route("/")
def home():
    return "Backend is working!"

# === Helper to generate a valid grid ===
def generate_grid(clubs, countries):
    valid_pairs = set(VALID_PAIRS.keys())
    valid_clubs = [club for club in clubs if any((c, club) in valid_pairs for c in countries)]
    valid_countries = [c for c in countries if any((c, club) in valid_pairs for club in clubs)]

    while True:
        selected_clubs = random.sample(valid_clubs, 3)
        selected_countries = random.sample(valid_countries, 3)
        if all((c, club) in valid_pairs for club in selected_clubs for c in selected_countries):
            return selected_clubs, selected_countries

# === Endpoint to generate a grid ===
@app.route("/generate-grid")
def generate_grid_endpoint():
    difficulty = request.args.get("difficulty", "easy")

    if difficulty == "medium":
        club_pool = medium_clubs
    elif difficulty == "hard":
        club_pool = hard_clubs
    else:
        club_pool = easy_clubs

    countries = [
        "England", "France", "Spain", "Germany", "Italy",
        "Portugal", "Argentina", "Brazil", "Netherlands"
    ]

    clubs, countries = generate_grid(club_pool, countries)

    return jsonify({
        "clubs": clubs,
        "countries": countries
    })

@app.route("/player-image/<int:player_id>")
def player_image(player_id):
    url = f"https://img.a.transfermarkt.technology/portrait/header/{player_id}.png"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return send_file(BytesIO(response.content), mimetype="image/png")
    except Exception:
        return "Image not available", 404


# === Endpoint to validate a player guess ===
@app.route("/submit-guess", methods=["POST"])
def submit_guess():
    data = request.get_json()
    club = data.get("club", "").strip()
    country = data.get("country", "").strip()
    player_input = data.get("player", "").strip()

    matches = df[(df["team"] == club) & (df["country"] == country)]

    for _, row in matches.iterrows():
        full_name = row["name"]
        parts = full_name.strip().split()
        alt_name = " ".join(parts[1:]) if len(parts) > 1 else parts[0]

        if player_input.lower() in (full_name.lower(), alt_name.lower()):
            return jsonify({"result": "correct", "player": full_name})

    return jsonify({"result": "incorrect"})

# === Run server ===
if __name__ == "__main__":
    app.run(debug=True)
