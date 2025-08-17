from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import random
import os
from valid_pairs import VALID_PAIRS
from difficulty import easy_clubs, medium_clubs, hard_clubs, easy_countries, medium_countries, hard_countries

import requests
from flask import send_file
from io import BytesIO

# Define app first
app = Flask(__name__)

# THEN enable CORS
CORS(app)

# === Load cleaned player data ===
DATA_PATH = os.path.join("data", "cleaned_players.csv")
df = pd.read_csv(DATA_PATH)

# === Game state tracking ===
active_games = {}

# === Root health check ===
@app.route("/")
def home():
    return "Backend is working!"

# === Helper to generate a valid grid ===
def generate_grid(clubs, countries):
    valid_pairs = set(VALID_PAIRS.keys())
    valid_clubs = [club for club in clubs if any((c, club) in valid_pairs for c in countries)]
    valid_countries = [c for c in countries if any((c, club) in valid_pairs for club in clubs)]

    # Ensure we have enough valid combinations
    if len(valid_clubs) < 3 or len(valid_countries) < 3:
        return None, None

    # Try multiple times to find a valid grid
    for _ in range(100):
        selected_clubs = random.sample(valid_clubs, 3)
        selected_countries = random.sample(valid_countries, 3)
        
        # Check if all combinations are valid
        if all((c, club) in valid_pairs for club in selected_clubs for c in selected_countries):
            return selected_clubs, selected_countries
    
    return None, None

# === Endpoint to generate a grid ===
@app.route("/generate-grid")
def generate_grid_endpoint():
    difficulty = request.args.get("difficulty", "easy")
    game_id = request.args.get("game_id", "default")

    if difficulty == "medium":
        club_pool = medium_clubs
    elif difficulty == "hard":
        club_pool = hard_clubs
    else:
        club_pool = easy_clubs

    if difficulty == "medium":
        country_pool = medium_countries
    elif difficulty == "hard":
        country_pool = hard_countries
    else:
        country_pool = easy_countries

    clubs, countries = generate_grid(club_pool, country_pool)
    
    if clubs is None:
        return jsonify({"error": "Could not generate valid grid"}), 400

    # Store game state
    active_games[game_id] = {
        "clubs": clubs,
        "countries": countries,
        "difficulty": difficulty,
        "guesses": {},
        "completed": False
    }

    return jsonify({
        "clubs": clubs,
        "countries": countries,
        "difficulty": difficulty,
        "game_id": game_id
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
    game_id = data.get("game_id", "default")

    # Validate game exists
    if game_id not in active_games:
        return jsonify({"error": "Game not found"}), 404

    game = active_games[game_id]
    
    # Validate the cell is in the current grid
    if club not in game["clubs"] or country not in game["countries"]:
        return jsonify({"error": "Invalid club or country for this grid"}), 400

    # Check if cell already filled
    cell_key = f"{club}|{country}"
    if cell_key in game["guesses"]:
        return jsonify({"error": "Cell already filled"}), 400

    # Find matching players
    matches = df[(df["team"] == club) & (df["country"] == country)]

    for _, row in matches.iterrows():
        full_name = row["name"]
        player_id = row.get("player_id", None)
        parts = full_name.strip().split()
        alt_name = " ".join(parts[1:]) if len(parts) > 1 else parts[0]

        if player_input.lower() in (full_name.lower(), alt_name.lower()):
            # Store the guess
            game["guesses"][cell_key] = {
                "name": full_name,
                "id": player_id,
                "club": club,
                "country": country
            }
            
            # Check if game is complete
            if len(game["guesses"]) == 9:
                game["completed"] = True
            
            return jsonify({
                "result": "correct", 
                "player": full_name,
                "id": player_id,
                "completed": game["completed"]
            })

    return jsonify({"result": "incorrect"})

# === Endpoint to get game state ===
@app.route("/game-state/<game_id>")
def get_game_state(game_id):
    if game_id not in active_games:
        return jsonify({"error": "Game not found"}), 404
    
    game = active_games[game_id]
    return jsonify({
        "clubs": game["clubs"],
        "countries": game["countries"],
        "difficulty": game["difficulty"],
        "guesses": game["guesses"],
        "completed": game["completed"]
    })

# === Endpoint to reset game ===
@app.route("/reset-game/<game_id>")
def reset_game(game_id):
    if game_id in active_games:
        del active_games[game_id]
    return jsonify({"message": "Game reset successfully"})

# === Endpoint to get hints ===
@app.route("/hint/<game_id>")
def get_hint(game_id):
    if game_id not in active_games:
        return jsonify({"error": "Game not found"}), 400
    
    game = active_games[game_id]
    
    # Get club and country from query parameters
    club = request.args.get('club')
    country = request.args.get('country')
    
    if not club or not country:
        return jsonify({"error": "Club and country parameters are required"}), 400
    
    # Debug: Print what we received vs what's in the game
    print(f"Received club: '{club}', country: '{country}'")
    print(f"Game clubs: {game['clubs']}")
    print(f"Game countries: {game['countries']}")
    
    # Validate the cell is in the current grid
    if club not in game["clubs"]:
        return jsonify({"error": f"Club '{club}' not found in grid. Available clubs: {game['clubs']}"}), 400
    
    if country not in game["countries"]:
        return jsonify({"error": f"Country '{country}' not found in grid. Available countries: {game['countries']}"}), 400
    
    # Check if cell already filled
    cell_key = f"{club}|{country}"
    if cell_key in game["guesses"]:
        return jsonify({"error": "Cell already filled"}), 400
    
    # Get a sample player for this specific combination
    matches = df[(df["team"] == club) & (df["country"] == country)]
    
    if len(matches) > 0:
        sample_player = matches.iloc[0]["name"]
        
        # Create hangman-like hint
        name_length = len(sample_player)
        # Reveal approximately 1/3 of the letters (minimum 2, maximum 5)
        letters_to_reveal = max(2, min(5, name_length // 3))
        
        # Create a list of positions to reveal
        positions = list(range(name_length))
        random.shuffle(positions)
        reveal_positions = positions[:letters_to_reveal]
        
        # Build the hint string
        hint_string = ""
        for i, char in enumerate(sample_player):
            if i in reveal_positions:
                hint_string += char
            elif char == " ":
                hint_string += " "
            else:
                hint_string += "_"
        
        return jsonify({
            "hint": f"Player name: {hint_string}",
            "sample_player": sample_player,
            "club": club,
            "country": country
        })
    
    return jsonify({"error": "No players found for this combination"}), 400

# === Run server ===
if __name__ == "__main__":
    app.run(debug=True, port=5001)
