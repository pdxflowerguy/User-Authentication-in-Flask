#!/usr/bin/env python3
"""
Database initialization script for production deployment
"""

from app import create_app, db
from models import User, ActivityLog
import os

def init_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Test database connection
            user_count = User.query.count()
            activity_count = ActivityLog.query.count()
            
            print(f"✓ Database connection verified")
            print(f"  - Users: {user_count}")
            print(f"  - Activity logs: {activity_count}")
            
            return True
            
        except Exception as e:
            print(f"✗ Database initialization failed: {e}")
            return False

if __name__ == "__main__":
    success = init_database()
    exit(0 if success else 1)
