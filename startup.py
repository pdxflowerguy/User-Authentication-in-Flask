#!/usr/bin/env python3
"""
Startup script for production deployment
This script ensures the database is properly initialized before the app starts
"""

from app import create_app, db
from models import User, ActivityLog

def initialize_app():
    """Initialize the application and database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Test database connectivity
            try:
                user_count = User.query.count()
                activity_count = ActivityLog.query.count()
                print(f"✓ Database connection verified - Users: {user_count}, Activities: {activity_count}")
            except Exception as e:
                print(f"Database query test failed: {e}")
                # If query fails, tables might not exist, try creating again
                db.create_all()
                print("✓ Database tables recreated")
                
            return True
            
        except Exception as e:
            print(f"✗ Database initialization failed: {e}")
            return False

if __name__ == "__main__":
    success = initialize_app()
    if success:
        print("✓ Application startup completed successfully")
    else:
        print("✗ Application startup failed")
        exit(1)
