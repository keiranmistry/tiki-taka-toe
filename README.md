# ⚽ Tiki Taka Toe

A beautiful, modern soccer-themed puzzle game where you fill a 3x3 grid with players who match the club and country combinations! Featuring stunning liquid glass UI design, user authentication, statistics tracking, and both guest and registered play modes.

![Game Preview](https://img.shields.io/badge/Status-Live%20Demo-brightgreen) ![React](https://img.shields.io/badge/React-18.0-blue) ![Flask](https://img.shields.io/badge/Flask-3.1-green) ![Python](https://img.shields.io/badge/Python-3.11-yellow)

## 🌐 Live Demo

**🎮 [Play Tiki Taka Toe Now!](https://tiki-taka-toe-kappa.vercel.app/)**

*Deployed with Vercel (Frontend) and Render (Backend)*

## 🎮 How to Play

### 🎯 **Core Gameplay**
1. **Choose Difficulty**: Easy (20pts), Medium (50pts), or Hard (100pts) per correct answer
2. **Select a Cell**: Click any empty square to choose a club-country combination
3. **Name the Player**: Enter a player who has played for that club AND is from that country
4. **Get Help**: Use hints when stuck (1st hint: -1 point, 2nd hint: -2 points, etc.)
5. **Complete the Grid**: Fill all 9 cells to achieve victory!

## ✨ Features

### 🔐 **Authentication System**
- **Guest Mode**: Play immediately without registration
- **User Accounts**: Create account with username and password (email optional)
- **Secure Login**: Industry-standard bcrypt password hashing
- **Session Management**: Persistent login across browser sessions
- **User Statistics**: Track your performance and progress

### 📊 **Statistics & Progress Tracking**
- **Game Statistics**: Total games, completed games, total score, average score
- **Performance by Difficulty**: See how you perform on Easy, Medium, and Hard
- **Recent Games**: View your last 10 games with detailed breakdowns
- **Success Rates**: Track completion rates and improvement over time
- **Local Stats**: Guest players get local statistics that persist in browser

### 🎯 **Game Modes & Difficulty**
- **Easy Mode**: Well-known clubs and countries (20 points per correct answer)
- **Medium Mode**: Popular clubs with good international presence (50 points)
- **Hard Mode**: Smaller clubs and less common countries (100 points)
- **Smart Grid Generation**: Ensures all combinations have valid players
- **Hint System**: Get help when stuck with point penalties

### 💡 **Smart Features**
- **Player Validation**: Real-time checking against 50,000+ professional players
- **Hint System**: Contextual help with increasing point costs
- **Game State Management**: Resume games across sessions
- **Error Handling**: Clear feedback for invalid guesses
- **Progress Tracking**: Visual indicators of completion status

### 🎨 **UI/UX Design**
- **Liquid Glass Design**: Modern glassmorphism with depth and transparency
- **Smooth Animations**: Subtle entrance effects and hover states
- **Color-coded Feedback**: Success (green), error (red), info (blue) states
- **Responsive Design**: Optimized for all screen sizes
- **Accessibility**: Keyboard navigation and screen reader support

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** (recommended: Python 3.11)
- **Node.js 14+** (recommended: Node.js 18+)
- **npm or yarn** package manager

### Backend Setup (Flask API)
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start the Flask server
python app.py
```

### Frontend Setup (React App)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

### Access the Game
- **🌐 Live Demo**: [https://tiki-taka-toe-kappa.vercel.app/](https://tiki-taka-toe-kappa.vercel.app/)
- **Local Development**:
  - **Frontend**: http://localhost:3000
  - **Backend API**: http://localhost:5001
  - **Database**: SQLite (development) or PostgreSQL/MySQL (production)

## 🏗️ Architecture

### Backend (Flask + SQLAlchemy)
- **Authentication**: Secure user registration, login, and session management
- **Database Models**: User, GameStats, UserSession with proper relationships
- **Game Logic**: Smart grid generation and player validation
- **API Endpoints**: RESTful API for all game operations
- **Security**: bcrypt password hashing and session tokens
- **Statistics**: Comprehensive user performance tracking

### Frontend (React + Modern CSS)
- **Component Architecture**: Modular, reusable React components
- **State Management**: React hooks for game and user state
- **Authentication Flow**: Seamless login/logout and guest mode
- **Responsive Design**: Mobile-first approach with breakpoints
- **Performance**: Optimized rendering and minimal re-renders

### Database Schema
```sql
Users: id, username, email, password_hash, created_at, last_login
GameStats: id, user_id, game_id, difficulty, score, hints_used, time_taken, completed, played_at
UserSessions: id, user_id, token, created_at, expires_at
```

## 📊 Game Data

The game uses comprehensive real soccer data:
- **Players**: 50,000+ professional players from major leagues
- **Clubs**: 200+ clubs across Premier League, La Liga, Serie A, Bundesliga, and more
- **Countries**: 100+ countries with international representation
- **Valid Combinations**: Pre-validated club-country pairs ensuring solvability
- **Player Images**: High-quality photos for visual feedback

## 🔄 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/stats` - Get user statistics

### Game Operations
- `GET /generate-grid` - Generate new game grid
- `POST /submit-guess` - Submit player guess
- `GET /game-state/<id>` - Get current game state
- `GET /hint/<id>` - Get hint for current game
- `GET /reset-game/<id>` - Reset game
- `GET /player-image/<id>` - Get player image

## 🎨 Design System

### Liquid Glass Aesthetics
- **Glassmorphism**: Translucent backgrounds with blur effects
- **Depth Layers**: Multiple z-index layers for visual hierarchy
- **Subtle Animations**: Smooth transitions without distraction
- **Color Palette**: Professional blues and whites with accent colors
- **Typography**: Champions font for headers, clean sans-serif for body

### Responsive Breakpoints
- **Mobile**: 320px - 768px (single column, stacked layout)
- **Tablet**: 768px - 1024px (two column grid)
- **Desktop**: 1024px+ (full three column layout)

## 🔒 Security Features

- **Password Security**: bcrypt hashing with salt
- **Session Management**: Secure token-based authentication
- **Input Validation**: Server-side validation for all inputs
- **CORS Protection**: Proper cross-origin request handling
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **XSS Protection**: Input sanitization and output encoding


## 📝 License

This project is open source and available under the [MIT License](LICENSE).
