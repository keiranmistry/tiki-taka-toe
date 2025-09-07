#!/usr/bin/env python3
"""
Database initialization script for Tiki Taka Toe
Run this script to create the database and tables
"""

import os
from app import create_app
from models import db, User, GameStats, UserSession

def init_database():
    """Initialize the database and create tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Create a test admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
        else:
            print("Admin user already exists")
        
        print("\nDatabase initialization complete!")
        print("You can now run the Flask application.")

if __name__ == "__main__":
    init_database()


