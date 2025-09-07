import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models import db, User, UserSession, GameStats

def generate_session_token(length=32):
    """Generate a random session token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_user_session(user_id):
    """Create a new user session"""
    # Clean up expired sessions first
    UserSession.query.filter(UserSession.expires_at < datetime.utcnow()).delete()
    db.session.commit()
    
    # Generate new session token
    session_token = generate_session_token()
    
    # Create session (expires in 7 days)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    session = UserSession(
        user_id=user_id,
        session_token=session_token,
        expires_at=expires_at
    )
    
    db.session.add(session)
    db.session.commit()
    
    return session_token

def get_user_from_session(session_token):
    """Get user from session token"""
    if not session_token:
        return None
    
    session = UserSession.query.filter_by(session_token=session_token).first()
    
    if not session or session.is_expired():
        return None
    
    return User.query.get(session.user_id)

def require_auth(f):
    """Decorator to require authentication for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        session_token = auth_header.split(' ')[1]
        user = get_user_from_session(session_token)
        
        if not user:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Add user to request context
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def register_user(username, password, email=None):
    """Register a new user"""
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return {'error': 'Username already exists'}, 400
    
    # Check email uniqueness only if provided
    if email and User.query.filter_by(email=email).first():
        return {'error': 'Email already exists'}, 400
    
    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        return {'message': 'User registered successfully', 'user_id': user.id}, 201
    except Exception as e:
        db.session.rollback()
        return {'error': 'Failed to register user'}, 500

def authenticate_user(username, password):
    """Authenticate a user and return session token"""
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return {'error': 'Invalid username or password'}, 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create session
    session_token = create_user_session(user.id)
    
    return {
        'message': 'Login successful',
        'session_token': session_token,
        'user': user.to_dict()
    }, 200

def logout_user(session_token):
    """Logout a user by removing their session"""
    session = UserSession.query.filter_by(session_token=session_token).first()
    
    if session:
        db.session.delete(session)
        db.session.commit()
    
    return {'message': 'Logout successful'}, 200

def get_user_stats(user_id):
    """Get comprehensive user statistics"""
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found'}, 404
    
    # Get all game stats for the user
    game_stats = GameStats.query.filter_by(user_id=user_id).all()
    
    # Calculate summary statistics
    total_games = len(game_stats)
    completed_games = len([g for g in game_stats if g.completed])
    total_score = sum(g.score for g in game_stats)
    total_hints_used = sum(g.hints_used for g in game_stats)
    total_hint_penalty = sum(g.hint_penalty for g in game_stats)
    
    # Calculate average score
    avg_score = total_score / total_games if total_games > 0 else 0
    
    # Get difficulty breakdown
    difficulty_stats = {}
    for stat in game_stats:
        diff = stat.difficulty
        if diff not in difficulty_stats:
            difficulty_stats[diff] = {'count': 0, 'total_score': 0, 'completed': 0}
        
        difficulty_stats[diff]['count'] += 1
        difficulty_stats[diff]['total_score'] += stat.score
        if stat.completed:
            difficulty_stats[diff]['completed'] += 1
    
    # Calculate averages for each difficulty
    for diff in difficulty_stats:
        count = difficulty_stats[diff]['count']
        difficulty_stats[diff]['avg_score'] = difficulty_stats[diff]['total_score'] / count if count > 0 else 0
        difficulty_stats[diff]['completion_rate'] = difficulty_stats[diff]['completed'] / count if count > 0 else 0
    
    return {
        'user': user.to_dict(),
        'summary': {
            'total_games': total_games,
            'completed_games': completed_games,
            'completion_rate': completed_games / total_games if total_games > 0 else 0,
            'total_score': total_score,
            'avg_score': round(avg_score, 2),
            'total_hints_used': total_hints_used,
            'total_hint_penalty': total_hint_penalty
        },
        'difficulty_breakdown': difficulty_stats,
        'recent_games': [stat.to_dict() for stat in sorted(game_stats, key=lambda x: x.played_at, reverse=True)[:10]]
    }, 200


