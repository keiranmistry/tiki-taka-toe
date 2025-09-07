import React, { useEffect, useState, useCallback } from 'react';
import './App.css';
import Auth from './components/Auth';
import UserStats from './components/UserStats';

function App() {
  // Authentication state
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showStats, setShowStats] = useState(false);

  // Game state
  const [clubs, setClubs] = useState([]);
  const [countries, setCountries] = useState([]);
  const [guesses, setGuesses] = useState({});
  const [gameId, setGameId] = useState(null);
  const [gameCompleted, setGameCompleted] = useState(false);
  const [score, setScore] = useState(0);
  
  // Input state
  const [clubInput, setClubInput] = useState('');
  const [countryInput, setCountryInput] = useState('');
  const [playerInput, setPlayerInput] = useState('');
  const [selectedCell, setSelectedCell] = useState(null);
  
  // UI state
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');
  const [loading, setLoading] = useState(false);
  const [difficulty, setDifficulty] = useState('easy');
  
  // Hint system
  const [showHint, setShowHint] = useState(false);
  const [hintText, setHintText] = useState('');
  const [hintDetails, setHintDetails] = useState(null);
  const [hintCounts, setHintCounts] = useState({});
  const [isFadingOut, setIsFadingOut] = useState(false);
  
  // Modal state
  const [showGiveUpConfirm, setShowGiveUpConfirm] = useState(false);
  
  // Stats tracking (local fallback)
  const [stats, setStats] = useState({
    totalGames: 0,
    completedGames: 0,
    totalScore: 0,
    averageScore: 0,
    bestScore: 0,
    gamesByDifficulty: { easy: 0, medium: 0, hard: 0 },
    totalHintsUsed: 0,
    currentStreak: 0,
    bestStreak: 0
  });

  // Check authentication on app load
  useEffect(() => {
    checkAuth();
  }, []);

  // Load stats on component mount
  useEffect(() => {
    loadStats();
  }, []);

  // Save stats whenever they change
  useEffect(() => {
    if (stats.totalGames > 0) {
      localStorage.setItem('tikiTakaToeStats', JSON.stringify(stats));
    }
  }, [stats]);

  const checkAuth = async () => {
    const sessionToken = localStorage.getItem('sessionToken');
    const userData = localStorage.getItem('user');
    
    if (sessionToken && userData) {
      try {
        // Verify the session is still valid
        const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/profile`, {
          headers: {
            'Authorization': `Bearer ${sessionToken}`,
          },
        });
        
        if (response.ok) {
          setUser(JSON.parse(userData));
        } else {
          // Session expired, clear local storage
          localStorage.removeItem('sessionToken');
          localStorage.removeItem('user');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('sessionToken');
        localStorage.removeItem('user');
      }
    }
    
    setIsLoading(false);
  };

  const handleLogin = (data) => {
    setUser(data.user);
    setIsLoading(false);
  };

  const handleGuest = () => {
    setUser({ id: null, username: 'Guest', isGuest: true });
    setIsLoading(false);
  };

  const handleLogout = () => {
    setUser(null);
    setShowStats(false);
    // Reset game state
    setClubs([]);
    setCountries([]);
    setGuesses({});
    setGameId(null);
    setGameCompleted(false);
    setScore(0);
    setSelectedCell(null);
    setMessage('');
  };

  // Function to convert country names to flag emojis
  const getCountryFlag = (countryName) => {
    const countryFlags = {
      "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
      "France": "🇫🇷",
      "Spain": "🇪🇸",
      "Germany": "🇩🇪",
      "Italy": "🇮🇹",
      "Portugal": "🇵🇹",
      "Argentina": "🇦🇷",
      "Brazil": "🇧🇷",
      "Netherlands": "🇳🇱",
      "Belgium": "🇧🇪",
      "Switzerland": "🇨🇭",
      "Austria": "🇦🇹",
      "Czech Republic": "🇨🇿",
      "Poland": "🇵🇱",
      "Hungary": "🇭🇺",
      "Romania": "🇷🇴",
      "Bulgaria": "🇧🇬",
      "Serbia": "🇷🇸",
      "Croatia": "🇭🇷",
      "Slovenia": "🇸🇮",
      "Slovakia": "🇸🇰",
      "Ukraine": "🇺🇦",
      "Russia": "🇷🇺",
      "Turkey": "🇹🇷",
      "Greece": "🇬🇷",
      "Norway": "🇳🇴",
      "Sweden": "🇸🇪",
      "Denmark": "🇩🇰",
      "Finland": "🇫🇮",
      "Iceland": "🇮🇸",
      "Estonia": "🇪🇪",
      "Latvia": "🇱🇻",
      "Lithuania": "🇱🇹",
      "Belarus": "🇧🇾",
      "Moldova": "🇲🇩",
      "Albania": "🇦🇱",
      "Montenegro": "🇲🇪",
      "Bosnia and Herzegovina": "🇧🇦",
      "North Macedonia": "🇲🇰",
      "Kosovo": "🇽🇰",
      "Luxembourg": "🇱🇺",
      "Malta": "🇲🇹",
      "Cyprus": "🇨🇾",
      "Georgia": "🇬🇪",
      "Armenia": "🇦🇲",
      "Azerbaijan": "🇦🇿",
      "Kazakhstan": "🇰🇿",
      "Uzbekistan": "🇺🇿",
      "Kyrgyzstan": "🇰🇬",
      "Tajikistan": "🇹🇯",
      "Turkmenistan": "🇹🇲",
      "Mongolia": "🇲🇳",
      "China": "🇨🇳",
      "Japan": "🇯🇵",
      "South Korea": "🇰🇷",
      "North Korea": "🇰🇵",
      "Vietnam": "🇻🇳",
      "Thailand": "🇹🇭",
      "Malaysia": "🇲🇾",
      "Singapore": "🇸🇬",
      "Indonesia": "🇮🇩",
      "Philippines": "🇵🇭",
      "India": "🇮🇳",
      "Pakistan": "🇵🇰",
      "Bangladesh": "🇧🇩",
      "Sri Lanka": "🇱🇰",
      "Nepal": "🇳🇵",
      "Bhutan": "🇧🇹",
      "Myanmar": "🇲🇲",
      "Laos": "🇱🇦",
      "Cambodia": "🇰🇭",
      "Brunei": "🇧🇳",
      "East Timor": "🇹🇱",
      "Papua New Guinea": "🇵🇬",
      "Fiji": "🇫🇯",
      "Vanuatu": "🇻🇺",
      "Solomon Islands": "🇸🇧",
      "New Caledonia": "🇳🇨",
      "Tahiti": "🇵🇫",
      "Samoa": "🇼🇸",
      "Tonga": "🇹🇴",
      "American Samoa": "🇦🇸",
      "Guam": "🇬🇺",
      "Northern Mariana Islands": "🇲🇵",
      "Palau": "🇵🇼",
      "Marshall Islands": "🇲🇭",
      "Micronesia": "🇫🇲",
      "Nauru": "🇳🇷",
      "Tuvalu": "🇹🇻",
      "Kiribati": "🇰🇮",
      "Wallis and Futuna": "🇼🇫",
      "Cook Islands": "🇨🇰",
      "Niue": "🇳🇺",
      "Tokelau": "🇹🇰"
    };
    
    return countryFlags[countryName] || countryName;
  };

  // Function to get club badges from Transfermarkt
  const getClubBadge = (clubName) => {
    // Map club names to Transfermarkt club IDs
    const clubIds = {
      // Premier League
      "Arsenal": "11",
      "Chelsea": "631",
      "Tottenham": "148",
      "Man United": "985",
      "Man City": "281",
      "Liverpool": "31",
      "Everton": "29",
      "Newcastle": "762",
      "Aston Villa": "405",
      "Brighton": "1237",
      "West Ham": "379",
      "Bournemouth": "989",
      "Brentford": "1148",
      "Crystal Palace": "873",
      "Fulham": "931",
      "Leicester": "1003",
      "Nottingham Forest": "703",
      "Southampton": "180",
      "Wolves": "543",
      
      // La Liga
      "Barcelona": "131",
      "Real Madrid": "418",
      "Atletico Madrid": "13",
      "Real Sociedad": "681",
      "Real Betis": "150",
      "Real Valladolid": "366",
      "Sevilla": "368",
      "Valencia": "1049",
      "Villarreal": "1050",
      "Athletic Bilbao": "621",
      "Celta Vigo": "940",
      "Espanyol": "714",
      "Getafe": "3709",
      "Girona": "12321",
      "Las Palmas": "472",
      "Mallorca": "237",
      "Osasuna": "331",
      "Rayo Vallecano": "367",
      "Alaves": "1108",
      "Cadiz": "536",
      
      // Bundesliga
      "Bayern Munich": "27",
      "Borussia Dortmund": "16",
      "Bayer Leverkusen": "15",
      "Leipzig": "23826",
      "Borussia Monchengladbach": "18",
      "Eintracht Frankfurt": "24",
      "VfB Stuttgart": "79",
      "VfL Wolfsburg": "82",
      "SC Freiburg": "60",
      "1. FC Heidenheim": "12321",
      "TSG Hoffenheim": "533",
      "1. FC Union Berlin": "89",
      "1. FC Koln": "3",
      "SV Werder Bremen": "86",
      "1. FSV Mainz 05": "39",
      "VfL Bochum": "2",
      "FC Augsburg": "16",
      "FC St. Pauli": "105",
      
      // Serie A
      "Juventus": "506",
      "Milan": "5",
      "Inter": "46",
      "Napoli": "6195",
      "Roma": "12",
      "Lazio": "398",
      "Atalanta": "800",
      "Fiorentina": "430",
      "Torino": "416",
      "Bologna": "1038",
      "Genoa": "252",
      "Monza": "12321",
      "Cagliari": "1390",
      "Empoli": "391",
      "Frosinone": "12321",
      "Lecce": "1005",
      "Salernitana": "12321",
      "Sassuolo": "6574",
      "Udinese": "410",
      "Verona": "276",
      "Como": "12321",
      
      // Ligue 1
      "PSG": "583",
      "Monaco": "162",
      "Marseille": "164",
      "Lyon": "1041",
      "Lille": "1082",
      "Lens": "1081",
      "Nice": "4171",
      "Reims": "1427",
      "Rennes": "273",
      "Strasbourg": "167",
      "Nantes": "995",
      "Montpellier": "969",
      "Toulouse": "415",
      "Brest": "12321",
      "Le Havre": "12321",
      "Metz": "347",
      "Clermont": "12321",
      "Lorient": "1420",
      
      // Other Major Clubs
      "Porto": "2120",
      "Benfica": "118",
      "Sporting CP": "2120",
      "Vitoria Guimaraes": "12321",
      "Ajax": "610",
      "Feyenoord": "234",
      "PSV": "383",
      "Club Brugge": "458",
      "Anderlecht": "261",
      "Standard Liege": "12321",
      "Red Bull Salzburg": "409",
      "Rapid Vienna": "12321",
      "Slavia Prague": "12321",
      "Sparta Prague": "12321",
      "Dinamo Zagreb": "12321",
      "Hajduk Split": "12321",
      "Ferencvaros": "12321",
      "Debrecen": "12321",
      "Legia Warsaw": "12321",
      "Lech Poznan": "12321",
      "Slovan Bratislava": "12321",
      "Spartak Moscow": "12321",
      "CSKA Moscow": "12321",
      "Lokomotiv Moscow": "12321",
      "Zenit St Petersburg": "12321",
      "Galatasaray": "12321",
      "Fenerbahce": "12321",
      "Besiktas": "12321",
      "Trabzonspor": "12321",
      "Olympiacos": "12321",
      "Panathinaikos": "12321",
      "AEK Athens": "12321",
      "PAOK Thessaloniki": "12321",
      "Rosenborg": "12321",
      "Molde": "12321",
      "Malmo": "12321",
      "AIK Stockholm": "12321",
      "Hammarby": "12321",
      "FC Copenhagen": "12321",
      "Midtjylland": "12321",
      "Brondby": "12321"
    };
    
    const clubId = clubIds[clubName];
    if (clubId) {
      return `https://tmssl.akamaized.net/images/wappen/head/${clubId}.png`;
    }
    
    return "⚽"; // Fallback for unknown clubs
  };

  const generateNewGame = useCallback(async (difficultyLevel = difficulty) => {
    try {
      setLoading(true);
      setMessage('');
      setMessageType('');
      setGuesses({});
      setGameCompleted(false);
      setScore(0);
      setSelectedCell(null);
      setClubInput('');
      setCountryInput('');
      setPlayerInput('');
      setShowHint(false);
      setHintText('');
      setHintDetails(null);
      setIsFadingOut(false); // Reset fade-out state
      setHintCounts({}); // Reset hint counts
      
      // Generate a unique game ID
      const newGameId = `game_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setGameId(newGameId);
      
      // Store the new game data
      const response = await fetch(`${process.env.REACT_APP_API_URL}/generate-grid?difficulty=${difficultyLevel}&game_id=${newGameId}`);
      const data = await response.json();
      
      if (response.ok) {
        setGameId(newGameId);
        setClubs(data.clubs);
        setCountries(data.countries);
        setDifficulty(data.difficulty);
        setMessage('🎮 New game generated! Click any square to start playing.');
        setMessageType('success');
      } else {
        setMessage(`❌ ${data.error}`);
        setMessageType('error');
      }
    } catch (error) {
      setMessage('❌ Error generating new game');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  }, [difficulty]);

  // Generate initial game when user is authenticated
  useEffect(() => {
    if (user && !isLoading) {
      generateNewGame('easy');
    }
  }, [user, isLoading, generateNewGame]);

  const handleCellClick = (club, country) => {
    if (!gameId) return;
    
    // Validate that this club and country are part of the current game
    if (!clubs.includes(club) || !countries.includes(country)) {
      setMessage(`❌ Invalid cell: ${club} (${country}) is not part of the current game`);
      setMessageType('error');
      return;
    }
    
    const key = `${club}|${country}`;
    const guess = guesses[key];
    
    if (guess) {
      setMessage('❌ This cell is already filled!');
      setMessageType('error');
      return;
    }
    
    setSelectedCell({ club, country });
    setClubInput(club);
    setCountryInput(country);
    setPlayerInput('');
    setMessage(`🎯 Selected: ${club} (${country})`);
    setMessageType('success');
    
    // Clear any existing hint when selecting a new cell
    setShowHint(false);
    setHintText('');
    setHintDetails(null);
    setIsFadingOut(false);
  };

  const handleGuess = async () => {
    if (!clubInput || !countryInput || !playerInput) {
      setMessage('❌ Please select a cell and enter a player name', 'error');
      return;
    }

    setLoading(true);
    try {
      const requestBody = {
        club: clubInput,
        country: countryInput,
        player: playerInput,
        game_id: gameId
      };

      // Add user_id if user is authenticated and not a guest
      if (user && !user.isGuest) {
        requestBody.user_id = user.id;
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL}/submit-guess`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestBody)
      });
      
      const data = await response.json();
      
      if (response.ok && data.result === "correct") {
        const key = `${clubInput}|${countryInput}`;
        setGuesses(prev => ({ 
          ...prev, 
          [key]: { 
            name: data.player, 
            id: data.id,
            club: clubInput,
            country: countryInput
          } 
        }));
        
        setScore(prev => prev + data.points_earned);
        setMessage(`✅ Correct! ${data.player} played for ${clubInput} and nationally represents ${countryInput}`);
        setMessageType('success');
        
        // Trigger fade-out animation
        setIsFadingOut(true);
        setTimeout(() => {
          setIsFadingOut(false);
          // Clear selection and inputs
          setSelectedCell(null);
          setClubInput('');
          setCountryInput('');
          setPlayerInput('');
        }, 500); // Match duration of fade-out animation
        
        if (data.completed) {
          setGameCompleted(true);
          setMessage('🎉 Congratulations! You completed the grid!');
          setMessageType('success');
          
          // Update stats for completed game
          const hintsUsed = Object.values(hintCounts).reduce((sum, count) => sum + count, 0);
          updateStats(true, score + data.points_earned, difficulty, hintsUsed);
        }
      } else if (response.status === 400) {
        setMessage(`❌ ${data.error}`);
        setMessageType('error');
      } else {
        setMessage('❌ Incorrect guess. Try again!');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('❌ Network error. Please try again.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const getHint = async () => {
    if (!gameId || !selectedCell) {
      setMessage('❌ Please select a square first');
      setMessageType('error');
      return;
    }

    // Check if we've reached the maximum hint count for this cell
    const cellKey = `${selectedCell.club}|${selectedCell.country}`;
    const currentHintCount = (hintCounts[cellKey] || 0) + 1;
    
    // Maximum 5 hints per cell (reveals up to 6 letters, leaving at least 1 hidden)
    if (currentHintCount > 5) {
      setMessage('💡 Maximum hints reached for this cell!');
      setMessageType('info');
      return;
    }

    try {
      setLoading(true);
      
              const response = await fetch(`${process.env.REACT_APP_API_URL}/hint/${gameId}?club=${encodeURIComponent(selectedCell.club)}&country=${encodeURIComponent(selectedCell.country)}&hint_count=${currentHintCount}`);
      const data = await response.json();
      
      if (response.ok) {
        setHintText(data.hint);
        setHintDetails({ 
          club: data.club, 
          country: data.country,
          hintCount: data.hint_count,
          totalLettersRevealed: data.total_letters_revealed,
          nameLength: data.name_length
        });
        setShowHint(true);
        
        // Update hint count for this cell
        setHintCounts(prev => ({
          ...prev,
          [cellKey]: currentHintCount
        }));
        
        // Penalty: 1 point for first hint, 2 for second, 3 for third, etc.
        const penalty = currentHintCount; // 1st hint = -1, 2nd hint = -2, etc.
        setScore(prev => Math.max(0, prev - penalty));
        
        setMessage(`💡 Hint ${currentHintCount} received! (-${penalty} points)`);
        setMessageType('info');
      } else {
        setMessage(`❌ ${data.error}`);
        setMessageType('error');
      }
    } catch (error) {
      setMessage('❌ Error getting hint');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleGiveUp = async () => {
    
    if (!gameId) {
      setMessage('❌ No active game to give up on');
      setMessageType('error');
      return;
    }

    try {
      setLoading(true);
      
              // Fetch all answers from the backend
        const response = await fetch(`${process.env.REACT_APP_API_URL}/give-up/${gameId}`);
      
      const data = await response.json();

      if (response.ok) {
        // Fill in all remaining cells with the correct answers
        const allAnswers = {};
        data.answers.forEach(answer => {
          const key = `${answer.club}|${answer.country}`;
          allAnswers[key] = {
            name: answer.player,
            id: answer.id,
            club: answer.club,
            country: answer.country
          };
        });
        
        // Merge with existing guesses to preserve any correct answers already given
        const mergedGuesses = { ...guesses, ...allAnswers };
        
        setGuesses(mergedGuesses);
        setGameCompleted(true);
        setMessage('🏳️ Game ended. Here are all the answers:');
        setMessageType('info');
        
        // Update stats for given up game
        const hintsUsed = Object.values(hintCounts).reduce((sum, count) => sum + count, 0);
        updateStats(false, score, difficulty, hintsUsed);
      } else {
        setMessage(`❌ ${data.error}`);
        setMessageType('error');
      }
    } catch (error) {
      setMessage('❌ Error giving up');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const confirmGiveUp = () => {
    setShowGiveUpConfirm(true);
  };

  const handleDifficultyChange = (newDifficulty) => {
    setDifficulty(newDifficulty);
    generateNewGame(newDifficulty);
  };

  const getCellContent = (club, country) => {
    const key = `${club}|${country}`;
    const guess = guesses[key];
    
    if (guess) {
      return (
        <div className="cell-content">
          <div className="player-name-display">
            <div className="player-name">
              {guess.name}
            </div>
          </div>
        </div>
      );
    }
    
    return <div className="empty-cell">___</div>;
  };

  const getCellClassName = (club, country) => {
    const key = `${club}|${country}`;
    const guess = guesses[key];
    const isSelected = selectedCell && selectedCell.club === club && selectedCell.country === country;
    
    let className = "grid-cell";
    
    if (guess) {
      className += " filled-cell";
    } else if (isSelected) {
      className += " selected-cell";
    } else {
      className += " clickable-cell";
    }
    
    return className;
  };

  // Function to update stats
  const updateStats = (gameCompleted, finalScore, difficulty, hintsUsed) => {
    setStats(prev => {
      const newTotalGames = prev.totalGames + 1;
      const newCompletedGames = prev.completedGames + (gameCompleted ? 1 : 0);
      const newTotalScore = prev.totalScore + finalScore;
      const newAverageScore = newTotalScore / newTotalGames;
      const newBestScore = Math.max(prev.bestScore, finalScore);
      const newGamesByDifficulty = {
        ...prev.gamesByDifficulty,
        [difficulty]: prev.gamesByDifficulty[difficulty] + 1
      };
      const newTotalHintsUsed = prev.totalHintsUsed + hintsUsed;
      
      // Update streaks
      let newCurrentStreak, newBestStreak;
      if (gameCompleted) {
        newCurrentStreak = prev.currentStreak + 1;
        newBestStreak = Math.max(prev.bestStreak, newCurrentStreak);
      } else {
        newCurrentStreak = 0;
        newBestStreak = prev.bestStreak;
      }
      
      return {
        totalGames: newTotalGames,
        completedGames: newCompletedGames,
        totalScore: newTotalScore,
        averageScore: Math.round(newAverageScore),
        bestScore: newBestScore,
        gamesByDifficulty: newGamesByDifficulty,
        totalHintsUsed: newTotalHintsUsed,
        currentStreak: newCurrentStreak,
        bestStreak: newBestStreak
      };
    });
  };

  // Function to load stats from localStorage
  const loadStats = () => {
    const savedStats = localStorage.getItem('tikiTakaToeStats');
    if (savedStats) {
      setStats(JSON.parse(savedStats));
    }
  };


  // Show loading screen while checking authentication
  if (isLoading) {
    return (
      <div className="app">
        <div className="loading-screen">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Show authentication screen if not logged in
  if (!user) {
    return <Auth onLogin={handleLogin} onGuest={handleGuest} />;
  }

  // Show stats screen if user wants to view stats
  if (showStats) {
    return (
      <div className="app">
        <UserStats user={user} onLogout={handleLogout} />
        <div className="stats-actions">
          <button 
            onClick={() => setShowStats(false)} 
            className="btn btn-primary"
          >
            Back to Game
          </button>
        </div>
      </div>
    );
  }

  // Show main game interface for authenticated users
  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>⚽ Soccer Tiki Taka Toe</h1>
          <p className="subtitle">Tic-Tac-Toe with a soccer-themed twist</p>
          
          {/* User info and controls */}
          <div className="user-controls">
            <div className="user-info">
              <span>Welcome, {user.username}! {user.isGuest && '(Guest)'}</span>
            </div>
            <div className="header-buttons">
              {!user.isGuest && (
                <button 
                  onClick={() => setShowStats(true)} 
                  className="btn btn-info"
                >
                  📊 My Stats
                </button>
              )}
              <button 
                onClick={handleLogout} 
                className="btn btn-secondary"
              >
                {user.isGuest ? 'Sign In' : 'Logout'}
              </button>
            </div>
          </div>
          
          {/* Quick Stats Preview */}
          {stats.totalGames > 0 && (
            <div className="quick-stats">
              <span className="stat-preview">🔥 {stats.currentStreak} streak</span>
              <span className="stat-preview">🏆 {stats.bestScore} best</span>
              <span className="stat-preview">📊 {stats.completedGames}/{stats.totalGames} wins</span>
            </div>
          )}
        </header>

        <div className="game-controls">
          <div className="difficulty-selector">
            <label>Difficulty:</label>
            <select 
              value={difficulty} 
              onChange={(e) => handleDifficultyChange(e.target.value)}
              disabled={loading}
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          
          <div className="score-display">
            <span>Score: {score}</span>
            {Object.keys(guesses).length > 0 && (
              <span className="progress-indicator">
                {Object.keys(guesses).length}/9 cells filled
              </span>
            )}
          </div>
          
          <button 
            onClick={() => generateNewGame(difficulty)} 
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Generating...' : '🔄 NEW Game'}
          </button>
          
          <button 
            onClick={confirmGiveUp} 
            className="btn btn-danger"
            disabled={loading || !gameId || gameCompleted}
          >
            {loading ? 'Giving Up...' : '🏳️ Give Up'}
          </button>
          
        </div>

        {/* Give Up Confirmation Modal */}
        {showGiveUpConfirm && (
          <div className="modal-overlay">
            <div className="modal-content">
              <h3>🏳️ Are you sure you want to give up?</h3>
              <p>This will reveal all the answers and end the game.</p>
              <div className="modal-buttons">
                <button onClick={handleGiveUp} className="btn btn-danger">Yes, Give Up</button>
                <button onClick={() => setShowGiveUpConfirm(false)} className="btn btn-secondary">Cancel</button>
              </div>
            </div>
          </div>
        )}


        {loading && <div className="loading">Loading...</div>}

        {clubs.length > 0 && countries.length > 0 && (
          <div className="game-grid">
            <div className="game-instructions">
              <p>Click on any empty square to select the club and country, then enter a player name!</p>
            </div>
            
            <table className="grid-table">
              <thead>
                <tr>
                  <th className="corner-cell"></th>
                  {countries.map(country => (
                    <th key={country} className="country-header">
                      <div className="country-flag">{getCountryFlag(country)}</div>
                      <div className="country-name">{country}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {clubs.map(club => (
                  <tr key={club}>
                    <td className="club-header">
                      <div className="club-badge"><img src={getClubBadge(club)} alt={club} /></div>
                      <div className="club-name">{club}</div>
                    </td>
                    {countries.map(country => (
                      <td 
                        key={`${club}|${country}`} 
                        className={getCellClassName(club, country)}
                        onClick={() => handleCellClick(club, country)}
                      >
                        {getCellContent(club, country)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {selectedCell && (
          <div className={`guess-section ${isFadingOut ? 'fade-out' : ''}`}>
            <h2>Enter Your Guess</h2>
            <div className="input-field-container">
            <div className="input-group">
                <label>Club</label>
              <input
                type="text"
                value={clubInput}
                className="input-field"
                disabled={loading}
                  readOnly
              />
              </div>
              <div className="input-group">
                <label>Country</label>
              <input
                type="text"
                value={countryInput}
                className="input-field"
                disabled={loading}
                  readOnly
              />
              </div>
              <div className="input-group">
                <label>Player Name</label>
              <input
                type="text"
                  placeholder="Enter player name"
                value={playerInput}
                onChange={e => setPlayerInput(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && playerInput.trim()) {
                      handleGuess();
                    }
                  }}
                className="input-field"
                disabled={loading}
              />
              </div>
              <div className="btn-container">
              <button 
                  type="button"
                onClick={handleGuess} 
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Submitting...' : 'Submit Guess'}
              </button>
              </div>
            </div>
            
            <div className="hint-section">
              <button 
                type="button"
                onClick={getHint} 
                className="btn btn-secondary"
                disabled={loading || !selectedCell || (hintCounts[`${selectedCell?.club}|${selectedCell?.country}`] || 0) >= 5}
              >
                {loading ? 'Getting Hint...' : 
                  (hintCounts[`${selectedCell?.club}|${selectedCell?.country}`] || 0) >= 5 ? 
                  '💡 Max Hints Reached' : 
                  `💡 Get Hint ${hintCounts[`${selectedCell?.club}|${selectedCell?.country}`] ? `#${hintCounts[`${selectedCell?.club}|${selectedCell?.country}`] + 1}` : ''}`
                }
              </button>
              {showHint && hintDetails && (
                <div className="hint-display">
                  <div className="hint-header">
                    <h3>💡 Hint #{hintDetails.hintCount}</h3>
                    <div className="hint-progress">
                      {hintDetails.totalLettersRevealed}/{hintDetails.nameLength} letters revealed
                      {(hintCounts[`${selectedCell?.club}|${selectedCell?.country}`] || 0) >= 5 && 
                        <span className="max-hints-reached"> • Max reached</span>
                      }
                    </div>
                  </div>
                  <div className="hint-text">{hintText}</div>
                  <div className="hint-location">
                    <span className="hint-club">{hintDetails.club}</span>
                    <span className="hint-separator">•</span>
                    <span className="hint-country">{hintDetails.country}</span>
                  </div>
                  {(hintCounts[`${selectedCell?.club}|${selectedCell?.country}`] || 0) >= 5 && (
                    <div className="hint-limit-message">
                      💡 You've reached the maximum hints for this cell. Try to guess the player!
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {gameCompleted && (
          <div className="completion-message">
            <h2>🎉 Game Complete!</h2>
            <p>Final Score: {score}</p>
            <button 
              onClick={() => generateNewGame(difficulty)} 
              className="btn btn-primary"
            >
              Play Again
            </button>
          </div>
        )}

        {message && (
          <div className={`message message-${messageType}`}>
            {message}
          </div>
        )}

        <div className="game-rules">
          <div className="rules-header">
            <h2>🎮 Game Rules</h2>
            <p className="rules-subtitle">Master the beautiful game of football knowledge</p>
          </div>
          
          <div className="rules-content">
            <div className="rules-section">
              <div className="rule-card">
                <div className="rule-icon">🎯</div>
                <div className="rule-content">
                  <h4>Select & Play</h4>
                  <p>Click any empty square to select the club and country combination</p>
                </div>
              </div>
              
              <div className="rule-card">
                <div className="rule-icon">⚽</div>
                <div className="rule-content">
                  <h4>Name the Player</h4>
                  <p>Enter a player who has played for that club AND is from that country</p>
                </div>
              </div>
              
              <div className="rule-card">
                <div className="rule-icon">📝</div>
                <div className="rule-content">
                  <h4>Flexible Naming</h4>
                  <p>Use full names or just last names - whatever works!</p>
                </div>
              </div>
            </div>
            
            <div className="rules-section">
              <div className="rule-card">
                <div className="rule-icon">💡</div>
                <div className="rule-content">
                  <h4>Get Help</h4>
                  <p>Use hints when stuck (1st hint: -1 point, 2nd hint: -2 points, etc.)</p>
                </div>
              </div>
              
              <div className="rule-card">
                <div className="rule-icon">🏆</div>
                <div className="rule-content">
                  <h4>Complete to Win</h4>
                  <p>Fill all 9 cells to achieve victory!</p>
                </div>
              </div>
              
              <div className="rule-card scoring-card">
                <div className="rule-icon">💯</div>
                <div className="rule-content">
                  <h4>Scoring System</h4>
                  <div className="scoring-details">
                    <div className="score-item">
                      <span className="difficulty easy">Easy</span>
                      <span className="points">20pts</span>
                    </div>
                    <div className="score-item">
                      <span className="difficulty medium">Medium</span>
                      <span className="points">50pts</span>
                    </div>
                    <div className="score-item">
                      <span className="difficulty hard">Hard</span>
                      <span className="points">100pts</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
