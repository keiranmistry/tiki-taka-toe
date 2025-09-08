from flask import Flask, request, jsonify, send_file
try:
    from flask_cors import CORS
except ImportError:
    # Fallback for environments where flask_cors might not be available
    print("Warning: flask_cors not available, CORS will be disabled")
    CORS = lambda app: None
import pandas as pd
import random
import os
from dotenv import load_dotenv
from datetime import datetime
from data.valid_pairs import VALID_PAIRS
from difficulty import easy_clubs, medium_clubs, hard_clubs, easy_countries, medium_countries, hard_countries
from models import db, User, GameStats, UserSession
from auth import require_auth, register_user, authenticate_user, logout_user, get_user_stats

import requests
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import text

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Load environment variables from a .env file if present (local dev convenience)
    load_dotenv()

    # Database URL with sensible default for local dev
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///tiki_taka_toe.db')
    # Normalize old postgres URLs if present (Railway/Heroku style)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Enable CORS
    CORS(app)
    
    return app

# Create the app instance
app = create_app()

# === Load cleaned player data ===
DATA_PATH = os.path.join("data", "cleaned_players.csv")
df = pd.read_csv(DATA_PATH)

# === Game state tracking ===
active_games = {}

# === Root health check ===
@app.route("/")
def home():
    return "Backend is working!"

# === Health check endpoint ===
@app.route("/health")
def health():
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "message": "Backend is working properly"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500

# === Authentication endpoints ===
@app.route("/auth/register", methods=["POST"])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get("username", "").strip()
    email = data.get("email", "").strip() or None  # Make email optional
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400
    
    result, status_code = register_user(username, password, email)
    return jsonify(result), status_code

@app.route("/auth/login", methods=["POST"])
def login():
    """Authenticate a user"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    result, status_code = authenticate_user(username, password)
    return jsonify(result), status_code

@app.route("/auth/logout", methods=["POST"])
@require_auth
def logout():
    """Logout a user"""
    auth_header = request.headers.get('Authorization')
    session_token = auth_header.split(' ')[1]
    
    result, status_code = logout_user(session_token)
    return jsonify(result), status_code

@app.route("/auth/profile")
@require_auth
def get_profile():
    """Get current user profile"""
    user = request.current_user
    return jsonify(user.to_dict())

@app.route("/auth/stats")
@require_auth
def get_stats():
    """Get current user statistics"""
    user = request.current_user
    result, status_code = get_user_stats(user.id)
    return jsonify(result), status_code

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

    # Debug: Print difficulty information
    print(f"Setting difficulty to: '{difficulty}' for game {game_id}")
    
    # Store game state
    active_games[game_id] = {
        "clubs": clubs,
        "countries": countries,
        "difficulty": difficulty,
        "guesses": {},
        "completed": False,
        "score": 0,
        "hints_used": 0,
        "total_hint_penalty": 0,
        "hint_positions": {},  # Track revealed letter positions for each cell
        "start_time": datetime.utcnow()  # Track when game started
    }

    return jsonify({
        "clubs": clubs,
        "countries": countries,
        "difficulty": difficulty,
        "game_id": game_id
    })

@app.route("/player-image/<int:player_id>")
def player_image(player_id):
    try:
        # Find the player by ID in our dataset
        player_row = df[df['player_id'] == player_id]
        if player_row.empty:
            return "Player not found", 404
        
        player_name = player_row.iloc[0]['name']
        
        # Search for player image using DuckDuckGo Images API
        # Format: "player name fotmob" for better football-specific results
        search_query = f"{player_name} fotmob"
        
        # DuckDuckGo Images API endpoint
        api_url = "https://api.duckduckgo.com/"
        params = {
            'q': search_query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract image results
        if 'Image' in data and data['Image']:
            image_url = data['Image']
            return jsonify({
                'image_url': image_url,
                'player_name': player_name,
                'search_query': search_query
            })
        elif 'RelatedTopics' in data and data['RelatedTopics']:
            # Look for image URLs in related topics
            for topic in data['RelatedTopics']:
                if 'Icon' in topic and topic['Icon']['URL']:
                    image_url = topic['Icon']['URL']
                    return jsonify({
                        'image_url': image_url,
                        'player_name': player_name,
                        'search_query': search_query
                    })
        
        # Fallback: return search query for manual search
        return jsonify({
            'search_query': search_query,
            'player_name': player_name,
            'message': 'No image found, but you can search manually'
        })
        
    except requests.RequestException as e:
        print(f"Error fetching player image: {e}")
        return jsonify({
            'error': 'Failed to fetch image',
            'player_name': player_name if 'player_name' in locals() else 'Unknown',
            'message': 'Try searching manually'
        }), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Try searching manually'
        }), 500

# === Endpoint to search for player image by name ===
@app.route("/search-player-image")
def search_player_image():
    try:
        player_name = request.args.get('name', '').strip()
        if not player_name:
            return jsonify({'error': 'Player name is required'}), 400
        
        # Try multiple search strategies for better results
        search_queries = [
            f"{player_name} fotmob",
            f"{player_name} football player",
            f"{player_name} soccer player",
            f"{player_name} transfermarkt"
        ]
        
        # DuckDuckGo Images API endpoint
        api_url = "https://api.duckduckgo.com/"
        
        for search_query in search_queries:
            params = {
                'q': search_query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            try:
                response = requests.get(api_url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                
                # Extract image results
                if 'Image' in data and data['Image']:
                    image_url = data['Image']
                    return jsonify({
                        'image_url': image_url,
                        'player_name': player_name,
                        'search_query': search_query,
                        'source': 'duckduckgo'
                    })
                elif 'RelatedTopics' in data and data['RelatedTopics']:
                    # Look for image URLs in related topics
                    for topic in data['RelatedTopics']:
                        if 'Icon' in topic and topic['Icon']['URL']:
                            image_url = topic['Icon']['URL']
                            return jsonify({
                                'image_url': image_url,
                                'player_name': player_name,
                                'search_query': search_query,
                                'source': 'duckduckgo'
                            })
            except:
                continue
        
        # If no images found, return search links for manual searching
        search_links = {
            'google': f"https://www.google.com/search?q={'+'.join(player_name.split())}+fotmob&tbm=isch",
            'duckduckgo': f"https://duckduckgo.com/?q={'+'.join(player_name.split())}+fotmob&iax=images&ia=images",
            'bing': f"https://www.bing.com/images/search?q={'+'.join(player_name.split())}+fotmob"
        }
        
        return jsonify({
            'player_name': player_name,
            'search_queries': search_queries,
            'search_links': search_links,
            'message': 'No image found automatically. Use the search links to find manually.',
            'tip': 'Try searching "player name fotmob" for best football-specific results'
        })
        
    except Exception as e:
        print(f"Unexpected error in search_player_image: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Try searching manually'
        }), 500

# === Helper to save game stats ===
def save_game_stats(game_id, user_id=None):
    """Save completed game statistics to database"""
    if game_id not in active_games:
        return False
    
    game = active_games[game_id]
    
    # Calculate time taken
    start_time = game.get("start_time")
    if start_time:
        time_taken = int((datetime.utcnow() - start_time).total_seconds())
    else:
        time_taken = 0
    
    try:
        # Create game stats record
        game_stat = GameStats(
            user_id=user_id,
            game_id=game_id,
            difficulty=game["difficulty"],
            score=game["score"],
            hints_used=game["hints_used"],
            hint_penalty=game["total_hint_penalty"],
            completed=game["completed"],
            time_taken=time_taken
        )
        
        db.session.add(game_stat)
        db.session.commit()
        
        print(f"Game stats saved for game {game_id}")
        return True
        
    except Exception as e:
        print(f"Error saving game stats: {e}")
        db.session.rollback()
        return False

# === Endpoint to validate a player guess ===
@app.route("/submit-guess", methods=["POST"])
def submit_guess():
    data = request.get_json()
    club = data.get("club", "").strip()
    country = data.get("country", "").strip()
    player_input = data.get("player", "").strip()
    game_id = data.get("game_id", "default")
    user_id = data.get("user_id")  # Optional user ID for tracking

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
            # Calculate points based on difficulty
            if game["difficulty"] == "easy":
                points = 20
            elif game["difficulty"] == "medium":
                points = 50
            else:  # hard
                points = 100
            
            # Add points to score
            game["score"] += points
            
            # Debug: Print scoring information
            print(f"Difficulty: {game['difficulty']}, Points calculated: {points}")
            print(f"Final score: {game['score']}")
            
            # Store the guess
            game["guesses"][cell_key] = {
                "name": full_name,
                "id": player_id if player_id else None,  # Handle case where ID might not exist
                "club": club,
                "country": country
            }
            
            # Check if game is complete
            if len(game["guesses"]) == 9:
                game["completed"] = True
                # Save game stats if user is logged in
                if user_id:
                    save_game_stats(game_id, user_id)
                else:
                    save_game_stats(game_id)  # Save as anonymous game
            
            return jsonify({
                "result": "correct", 
                "player": full_name,
                "id": player_id,
                "completed": game["completed"],
                "score": game["score"],
                "points_earned": points
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
        "completed": game["completed"],
        "score": game["score"],
        "total_hint_penalty": game["total_hint_penalty"]
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
    hint_count = int(request.args.get('hint_count', 1))  # Default to 1 if not provided

    if not club or not country:
        return jsonify({"error": "Club and country parameters are required"}), 400

    # Debug: Print what we received vs what's in the game
    print(f"Received club: '{club}', country: '{country}', hint_count: {hint_count}")
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

        # Create cumulative hangman-like hint that builds upon previous hints
        name_length = len(sample_player)
        
        # Get or create the hint positions for this cell
        cell_key = f"{club}|{country}"
        if cell_key not in game["hint_positions"]:
            game["hint_positions"][cell_key] = set()
        
        previously_revealed = game["hint_positions"][cell_key]
        
        # Apply hint penalty based on hint count
        hint_penalty = hint_count  # 1st hint = -1, 2nd hint = -2, etc.
        game["score"] = max(0, game["score"] - hint_penalty)  # Don't go below 0
        game["total_hint_penalty"] += hint_penalty
        game["hints_used"] += 1
        
        # Calculate how many new letters to reveal
        if hint_count == 1:
            new_letters_to_reveal = 2
        else:
            # Add 1-2 more random letters for each additional hint
            new_letters_to_reveal = random.randint(1, 2)
        
        # Find positions that haven't been revealed yet
        available_positions = [i for i in range(name_length) if i not in previously_revealed]
        
        # Randomly select new positions to reveal
        if available_positions:
            random.shuffle(available_positions)
            new_reveal_positions = available_positions[:new_letters_to_reveal]
            
            # Add new positions to the previously revealed set
            previously_revealed.update(new_reveal_positions)
        else:
            new_reveal_positions = []

        hint_string = ""
        for i, char in enumerate(sample_player):
            if i in previously_revealed:
                hint_string += char
            elif char == " ":
                hint_string += " "
            else:
                hint_string += "_"

        return jsonify({
            "hint": f"Player name: {hint_string}",
            "sample_player": sample_player,
            "club": club,
            "country": country,
            "hint_count": hint_count,
            "total_letters_revealed": len(previously_revealed),
            "name_length": name_length,
            "current_score": game["score"],
            "hint_penalty": hint_penalty,
            "total_hint_penalty": game["total_hint_penalty"]
        })

    return jsonify({"error": "No players found for this combination"}), 400

@app.route("/give-up/<game_id>")
def give_up(game_id):
    if game_id not in active_games:
        return jsonify({"error": "Game not found"}), 400

    game = active_games[game_id]
    
    # Get all the correct answers for the current grid
    answers = []
    for club in game["clubs"]:
        for country in game["countries"]:
            # Get a sample player for this combination
            matches = df[(df["team"] == club) & (df["country"] == country)]
            
            if len(matches) > 0:
                sample_player = matches.iloc[0]
                answers.append({
                    "club": club,
                    "country": country,
                    "player": sample_player["name"],
                    "id": sample_player.get("id", None)  # Make ID optional
                })
    
    return jsonify({
        "answers": answers,
        "message": "All answers revealed"
    })

# === Initialize database tables ===
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# === Run server ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
