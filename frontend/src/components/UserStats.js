import React, { useState, useEffect } from 'react';
import './UserStats.css';

const UserStats = ({ user, onLogout }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUserStats();
  }, []);

  const fetchUserStats = async () => {
    try {
      const sessionToken = localStorage.getItem('sessionToken');
      if (!sessionToken) {
        setError('No session token found');
        setLoading(false);
        return;
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/stats`, {
        headers: {
          'Authorization': `Bearer ${sessionToken}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        setError('Failed to fetch stats');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      const sessionToken = localStorage.getItem('sessionToken');
      if (sessionToken) {
        await fetch(`${process.env.REACT_APP_API_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${sessionToken}`,
          },
        });
      }
      
      localStorage.removeItem('sessionToken');
      localStorage.removeItem('user');
      onLogout();
    } catch (err) {
      console.error('Logout error:', err);
      // Still logout locally even if server request fails
      localStorage.removeItem('sessionToken');
      localStorage.removeItem('user');
      onLogout();
    }
  };

  if (loading) {
    return (
      <div className="stats-container">
        <div className="loading">Loading stats...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stats-container">
        <div className="error">Error: {error}</div>
        <button onClick={fetchUserStats} className="retry-button">Retry</button>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="stats-container">
        <div className="error">No stats available</div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>📊 Your Game Statistics</h1>
          <p className="subtitle">Track your progress and performance</p>
          
          <div className="user-controls">
            <div className="user-info">
              <span>Welcome back, {user.username}!</span>
            </div>
            <div className="header-buttons">
              <button 
                onClick={handleLogout} 
                className="btn btn-danger"
              >
                🚪 Logout
              </button>
            </div>
          </div>
        </header>

        <div className="stats-dashboard">
          {/* Summary Cards */}
          <div className="stats-summary">
            <div className="stat-card">
              <div className="stat-icon">🎮</div>
              <div className="stat-content">
                <div className="stat-number">{stats.summary.total_games}</div>
                <div className="stat-label">Total Games</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">🏆</div>
              <div className="stat-content">
                <div className="stat-number">{stats.summary.completed_games}</div>
                <div className="stat-label">Completed</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">💯</div>
              <div className="stat-content">
                <div className="stat-number">{stats.summary.total_score}</div>
                <div className="stat-label">Total Score</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <div className="stat-number">{Math.round(stats.summary.avg_score)}</div>
                <div className="stat-label">Avg Score</div>
              </div>
            </div>
          </div>

          {/* Performance by Difficulty */}
          <div className="difficulty-section">
            <h2>🎯 Performance by Difficulty</h2>
            {Object.entries(stats.difficulty_breakdown).length > 0 ? (
              <div className="difficulty-grid">
                {Object.entries(stats.difficulty_breakdown).map(([difficulty, data]) => (
                  <div key={difficulty} className="difficulty-card">
                    <div className="difficulty-header">
                      <h3>{difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}</h3>
                      <div className="difficulty-icon">
                        {difficulty === 'easy' ? '🟢' : difficulty === 'medium' ? '🟡' : '🔴'}
                      </div>
                    </div>
                    <div className="difficulty-metrics">
                      <div className="metric">
                        <span className="metric-label">Games</span>
                        <span className="metric-value">{data.count || data.games || 0}</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Completed</span>
                        <span className="metric-value">{data.completed || 0}</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Avg Score</span>
                        <span className="metric-value">{Math.round(data.avg_score || 0)}</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Success Rate</span>
                        <span className="metric-value">{Math.round((data.completion_rate || 0) * 100)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-data">
                <p>No games played yet. Start playing to see your performance!</p>
              </div>
            )}
          </div>

          {/* Recent Games */}
          <div className="recent-games-section">
            <h2>🕒 Recent Games</h2>
            {stats.recent_games.length > 0 ? (
              <div className="games-list">
                {stats.recent_games.map((game) => (
                  <div key={game.id} className="game-item">
                    <div className="game-header">
                      <div className="game-difficulty">
                        {game.difficulty === 'easy' ? '🟢' : game.difficulty === 'medium' ? '🟡' : '🔴'}
                        <span>{game.difficulty.toUpperCase()}</span>
                      </div>
                      <div className="game-score">{game.score} pts</div>
                    </div>
                    <div className="game-details">
                      <div className="game-stat">
                        <span className="stat-icon">💡</span>
                        <span>Hints: {game.hints_used}</span>
                      </div>
                      <div className="game-stat">
                        <span className="stat-icon">⏱️</span>
                        <span>Time: {Math.floor(game.time_taken / 60)}m {game.time_taken % 60}s</span>
                      </div>
                      <div className={`game-status ${game.completed ? 'completed' : 'incomplete'}`}>
                        <span className="status-icon">{game.completed ? '✅' : '❌'}</span>
                        <span>{game.completed ? 'Completed' : 'Incomplete'}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-data">
                <p>🎮 No games played yet. Start playing to see your recent games!</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserStats;


