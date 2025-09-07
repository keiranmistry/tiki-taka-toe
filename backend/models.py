from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # Made optional
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship to game stats
    game_stats = db.relationship('GameStats', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user object to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class GameStats(db.Model):
    __tablename__ = 'game_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    hint_penalty = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    time_taken = db.Column(db.Integer, default=0)  # in seconds
    played_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert game stats object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'game_id': self.game_id,
            'difficulty': self.difficulty,
            'score': self.score,
            'hints_used': self.hints_used,
            'hint_penalty': self.hint_penalty,
            'completed': self.completed,
            'time_taken': self.time_taken,
            'played_at': self.played_at.isoformat() if self.played_at else None
        }

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def is_expired(self):
        """Check if the session has expired"""
        return datetime.utcnow() > self.expires_at


