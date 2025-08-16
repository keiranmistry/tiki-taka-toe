import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [clubs, setClubs] = useState([]);
  const [countries, setCountries] = useState([]);
  const [guesses, setGuesses] = useState({});
  const [clubInput, setClubInput] = useState('');
  const [countryInput, setCountryInput] = useState('');
  const [playerInput, setPlayerInput] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');
  const [difficulty, setDifficulty] = useState('easy');
  const [gameId, setGameId] = useState(null);
  const [gameCompleted, setGameCompleted] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [hintText, setHintText] = useState('');
  const [loading, setLoading] = useState(false);
  const [score, setScore] = useState(0);

  const generateNewGame = async (selectedDifficulty) => {
    setLoading(true);
    setMessage('');
    setGuesses({});
    setGameCompleted(false);
    setScore(0);
    setShowHint(false);
    
    const newGameId = `game_${Date.now()}`;
    setGameId(newGameId);
    
    try {
      const response = await fetch(`http://127.0.0.1:5001/generate-grid?difficulty=${selectedDifficulty}&game_id=${newGameId}`);
      const data = await response.json();
      
      if (response.ok) {
        setClubs(data.clubs);
        setCountries(data.countries);
        setDifficulty(data.difficulty);
        setMessage(`🎮 New ${data.difficulty} game started! Fill all 9 cells to win!`);
        setMessageType('success');
      } else {
        setMessage(`❌ Error: ${data.error}`);
        setMessageType('error');
      }
    } catch (error) {
      setMessage('❌ Network error. Please try again.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generateNewGame('easy');
  }, []);

  const handleGuess = async () => {
    if (!clubInput || !countryInput || !playerInput) {
      setMessage('❌ Please fill in all fields', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:5001/submit-guess", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          club: clubInput,
          country: countryInput,
          player: playerInput,
          game_id: gameId
        })
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
        
        setScore(prev => prev + 10);
        setMessage(`✅ Correct! ${data.player} played for ${clubInput} and is from ${countryInput}`);
        setMessageType('success');
        
        if (data.completed) {
          setGameCompleted(true);
          setMessage('🎉 Congratulations! You completed the grid!');
          setMessageType('success');
        }
        
        // Clear inputs
        setClubInput('');
        setCountryInput('');
        setPlayerInput('');
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
    if (!gameId) return;
    
    try {
      const response = await fetch(`http://127.0.0.1:5001/hint/${gameId}`);
      const data = await response.json();
      
      if (response.ok) {
        setHintText(data.hint);
        setShowHint(true);
        setScore(prev => Math.max(0, prev - 2)); // Penalty for using hint
      } else {
        setMessage(`❌ ${data.error}`);
        setMessageType('error');
      }
    } catch (error) {
      setMessage('❌ Error getting hint');
      setMessageType('error');
    }
  };

  const resetGame = async () => {
    if (!gameId) return;
    
    try {
      await fetch(`http://127.0.0.1:5001/reset-game/${gameId}`);
      generateNewGame(difficulty);
    } catch (error) {
      setMessage('❌ Error resetting game');
      setMessageType('error');
    }
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
          <div className="image-container">
            <img
              src={`https://img.a.transfermarkt.technology/portrait/header/${guess.id}.jpg`}
              alt={guess.name}
              className="player-image"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
              onLoad={(e) => {
                e.target.style.display = 'block';
                e.target.nextSibling.style.display = 'none';
              }}
            />
            <div className="player-name fallback-name">
              {guess.name}
            </div>
          </div>
        </div>
      );
    }
    
    return <div className="empty-cell">___</div>;
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>⚽ Tiki Taka Toe</h1>
          <p className="subtitle">Fill the grid with players who match the club and country!</p>
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
          </div>
          
          <button 
            className="btn btn-secondary" 
            onClick={resetGame}
            disabled={loading}
          >
            🔄 New Game
          </button>
        </div>

        {loading && <div className="loading">Loading...</div>}

        {clubs.length > 0 && countries.length > 0 && (
          <div className="game-grid">
            <table className="grid-table">
              <thead>
                <tr>
                  <th className="corner-cell"></th>
                  {countries.map(country => (
                    <th key={country} className="country-header">
                      <div className="country-name">{country}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {clubs.map(club => (
                  <tr key={club}>
                    <td className="club-header">
                      <div className="club-name">{club}</div>
                    </td>
                    {countries.map(country => (
                      <td key={`${club}|${country}`} className="grid-cell">
                        {getCellContent(club, country)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!gameCompleted && (
          <div className="guess-section">
            <h2>Enter Your Guess</h2>
            <div className="input-group">
              <input
                type="text"
                placeholder="Club"
                value={clubInput}
                onChange={e => setClubInput(e.target.value)}
                className="input-field"
                disabled={loading}
              />
              <input
                type="text"
                placeholder="Country"
                value={countryInput}
                onChange={e => setCountryInput(e.target.value)}
                className="input-field"
                disabled={loading}
              />
              <input
                type="text"
                placeholder="Player Name"
                value={playerInput}
                onChange={e => setPlayerInput(e.target.value)}
                className="input-field"
                disabled={loading}
              />
              <button 
                onClick={handleGuess} 
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Submitting...' : 'Submit Guess'}
              </button>
            </div>
            
            <div className="hint-section">
              <button 
                onClick={getHint} 
                className="btn btn-hint"
                disabled={loading || showHint}
              >
                💡 Get Hint (-2 points)
              </button>
              {showHint && (
                <div className="hint-text">
                  {hintText}
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

        <div className="game-info">
          <h3>How to Play:</h3>
          <ul>
            <li>Fill each cell with a player who has played for the club AND is from the country</li>
            <li>You can use full names or last names</li>
            <li>Get hints if you're stuck (costs 2 points)</li>
            <li>Complete all 9 cells to win!</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;
