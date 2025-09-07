import React, { useState } from 'react';
import './Auth.css';

const Auth = ({ onLogin, onGuest }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!isLogin && formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        setLoading(false);
        return;
      }

      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = { username: formData.username, password: formData.password };

      const response = await fetch(`${process.env.REACT_APP_API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        if (isLogin) {
          // Store session token
          localStorage.setItem('sessionToken', data.session_token);
          localStorage.setItem('user', JSON.stringify(data.user));
          onLogin(data);
        } else {
          // Switch to login after successful registration
          setIsLogin(true);
          setFormData({ username: '', password: '', confirmPassword: '' });
          setError('Registration successful! Please log in.');
        }
      } else {
        setError(data.error || 'An error occurred');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setFormData({ username: '', password: '', confirmPassword: '' });
  };

  const handleGuestMode = () => {
    onGuest();
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-container">
        <div className="auth-header">
          <h1>⚽ Soccer Tiki Taka Toe</h1>
          <p className="subtitle">Tic-Tac-Toe with a soccer-themed twist</p>
          <p className="auth-description">
            Sign in to track your progress, compete with friends, and see detailed statistics!
          </p>
        </div>

        <div className="auth-card">
          <div className="auth-card-header">
            <h2>{isLogin ? '🔐 Login' : '📝 Register'}</h2>
            <p className="auth-subtitle">
              {isLogin ? 'Welcome back! Sign in to continue your journey.' : 'Join the game! Create your account to start tracking progress.'}
            </p>
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="username">👤 Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                disabled={loading}
                placeholder="Enter your username"
                className="input-field"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">🔒 Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                disabled={loading}
                minLength={6}
                placeholder="Enter your password"
                className="input-field"
              />
            </div>

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="confirmPassword">🔒 Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  required
                  disabled={loading}
                  minLength={6}
                  placeholder="Confirm your password"
                  className="input-field"
                />
              </div>
            )}

            <button type="submit" className="btn btn-primary auth-submit" disabled={loading}>
              {loading ? '⏳ Loading...' : (isLogin ? '🚀 Login' : '✨ Register')}
            </button>
          </form>

          <div className="auth-divider">
            <span>or</span>
          </div>

          <button 
            type="button" 
            onClick={handleGuestMode} 
            className="btn btn-success guest-button"
            disabled={loading}
          >
            🎮 Play as Guest
          </button>

          <div className="auth-toggle">
            <p>
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <button type="button" onClick={toggleMode} className="toggle-button">
                {isLogin ? '📝 Register' : '🔐 Login'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;


