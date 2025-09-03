def deploy():
        """Run deployment tasks."""
        from app import create_app, db
        from flask_migrate import upgrade, migrate, init, stamp
        from models import User, ActivityLog
        import os

        app = create_app()
        with app.app_context():
                try:
                        # Create all tables first
                        db.create_all()
                        print("✓ Database tables created successfully")
                        
                        # Check if migrations directory exists
                        if not os.path.exists('migrations'):
                                print("Initializing migrations...")
                                init()
                                stamp()
                        
                        # Generate and apply migrations
                        try:
                                # Only migrate if there are changes
                                migrate(message="Auto migration")
                                upgrade()
                                print("✓ Database migrations applied successfully")
                        except Exception as e:
                                print(f"Migration info: {e}")
                                # Try to just upgrade if migration fails
                                try:
                                        upgrade()
                                        print("✓ Database upgrade completed")
                                except Exception as e2:
                                        print(f"Migration note: {e2}")
                        
                        # Verify database
                        user_count = User.query.count()
                        activity_count = ActivityLog.query.count()
                        print(f"✓ Database verified - Users: {user_count}, Activities: {activity_count}")
                        
                except Exception as e:
                        print(f"✗ Deployment failed: {e}")
                        raise

if __name__ == "__main__":
        deploy()
        