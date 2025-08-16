# ⚽ Tiki Taka Toe

A fun soccer-themed puzzle game where you fill a 3x3 grid with players who match the club and country combinations!

## 🎮 How to Play

1. **Choose Difficulty**: Easy, Medium, or Hard
2. **Fill the Grid**: Each cell needs a player who has played for the club AND is from the country
3. **Make Guesses**: Enter club, country, and player name
4. **Get Hints**: Use hints if you're stuck (costs 2 points)
5. **Complete the Grid**: Fill all 9 cells to win!

## ✨ Features

### 🎯 **Game Modes**
- **Easy**: Well-known clubs and countries
- **Medium**: Popular clubs with good international presence  
- **Hard**: Smaller clubs and less common countries

### 🏆 **Scoring System**
- **Correct Guess**: +10 points
- **Hint Used**: -2 points
- **Goal**: Complete the grid with the highest score!

### 💡 **Smart Features**
- **Hints System**: Get help when stuck
- **Player Images**: See actual player photos when correct
- **Game State**: Track progress and resume games
- **Validation**: Ensures all grid combinations are valid
- **Responsive Design**: Works on all devices

### 🔧 **Technical Improvements**
- **Better Grid Generation**: Ensures all combinations have valid players
- **Game State Management**: Track multiple games simultaneously
- **Error Handling**: Better user feedback and validation
- **Performance**: Optimized data loading and processing

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Access the Game
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 🏗️ Architecture

### Backend (Flask)
- **Grid Generation**: Smart algorithm ensuring valid combinations
- **Player Validation**: Check guesses against real player data
- **Game State**: Track multiple active games
- **Hints System**: Provide helpful suggestions
- **API Endpoints**: RESTful API for game operations

### Frontend (React)
- **Modern UI**: Beautiful, responsive design
- **State Management**: React hooks for game logic
- **Real-time Updates**: Live score and progress tracking
- **Mobile First**: Optimized for all screen sizes

## 📊 Game Data

The game uses real soccer data including:
- **Players**: 50,000+ professional players
- **Clubs**: 200+ clubs across multiple leagues
- **Countries**: 100+ countries represented
- **Valid Combinations**: Pre-validated club-country pairs

## 🎨 UI/UX Features

- **Gradient Backgrounds**: Modern, attractive design
- **Smooth Animations**: Fade-in effects and hover states
- **Responsive Grid**: Adapts to different screen sizes
- **Color-coded Messages**: Success, error, and info states
- **Interactive Elements**: Hover effects and focus states

## 🔄 API Endpoints

- `GET /generate-grid` - Generate new game grid
- `POST /submit-guess` - Submit player guess
- `GET /game-state/<id>` - Get current game state
- `GET /hint/<id>` - Get hint for current game
- `GET /reset-game/<id>` - Reset game
- `GET /player-image/<id>` - Get player image

## 🚧 Future Enhancements

- [ ] **Multiplayer Mode**: Play with friends
- [ ] **Leaderboards**: Global and local rankings
- [ ] **Achievements**: Unlock badges and rewards
- [ ] **Custom Grids**: User-created challenges
- [ ] **Statistics**: Track performance over time
- [ ] **Offline Mode**: Play without internet

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Soccer data from Transfermarkt
- Player images from official sources
- Community feedback and suggestions

---

**Enjoy playing Tiki Taka Toe! ⚽🎯**