
#!/usr/bin/env python3

from app import create_app, db, bcrypt
from models import User, ActivityLog
from datetime import datetime, timedelta

def seed_database():
    """Seed the database with initial data."""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        ActivityLog.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create admin user
        print("Creating admin user...")
        admin_user = User(
            username='admin',
            email='admin@dashboard.com',
            pwd=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            first_name='System',
            last_name='Administrator',
            phone='+1-555-0100',
            is_admin=True,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        db.session.add(admin_user)
        
        # Create test user (as requested - but keep credentials hidden)
        test_user = User(
            username='testuser',
            email='john@doe.com',
            pwd=bcrypt.generate_password_hash('johndoe123').decode('utf-8'),
            first_name='John',
            last_name='Doe',
            phone='+1-555-0101',
            is_admin=True,  # Admin privileges for testing
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=25)
        )
        db.session.add(test_user)
        
        # Create sample regular users
        print("Creating sample users...")
        sample_users = [
            {
                'username': 'alice_smith',
                'email': 'alice.smith@email.com',
                'pwd': bcrypt.generate_password_hash('password123').decode('utf-8'),
                'first_name': 'Alice',
                'last_name': 'Smith',
                'phone': '+1-555-0102',
                'is_admin': False,
                'is_active': True,
                'created_at': datetime.utcnow() - timedelta(days=20)
            },
            {
                'username': 'bob_jones',
                'email': 'bob.jones@email.com',
                'pwd': bcrypt.generate_password_hash('password123').decode('utf-8'),
                'first_name': 'Bob',
                'last_name': 'Jones',
                'phone': '+1-555-0103',
                'is_admin': False,
                'is_active': True,
                'created_at': datetime.utcnow() - timedelta(days=15)
            },
            {
                'username': 'carol_white',
                'email': 'carol.white@email.com',
                'pwd': bcrypt.generate_password_hash('password123').decode('utf-8'),
                'first_name': 'Carol',
                'last_name': 'White',
                'phone': '+1-555-0104',
                'is_admin': False,
                'is_active': True,
                'created_at': datetime.utcnow() - timedelta(days=10)
            },
            {
                'username': 'david_brown',
                'email': 'david.brown@email.com',
                'pwd': bcrypt.generate_password_hash('password123').decode('utf-8'),
                'first_name': 'David',
                'last_name': 'Brown',
                'phone': '+1-555-0105',
                'is_admin': False,
                'is_active': False,  # Inactive user for testing
                'created_at': datetime.utcnow() - timedelta(days=5)
            },
            {
                'username': 'emily_davis',
                'email': 'emily.davis@email.com',
                'pwd': bcrypt.generate_password_hash('password123').decode('utf-8'),
                'first_name': 'Emily',
                'last_name': 'Davis',
                'phone': '+1-555-0106',
                'is_admin': False,
                'is_active': True,
                'created_at': datetime.utcnow() - timedelta(days=3)
            }
        ]
        
        for user_data in sample_users:
            user = User(**user_data)
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(sample_users) + 2} users successfully!")
        
        # Create sample activity logs
        print("Creating sample activity logs...")
        users = User.query.all()
        
        sample_activities = []
        for i, user in enumerate(users):
            # Login activities
            for j in range(3):
                activity = ActivityLog(
                    user_id=user.id,
                    action='Login',
                    description='User logged in successfully',
                    ip_address=f'192.168.1.{10 + i + j}',
                    timestamp=datetime.utcnow() - timedelta(days=j+1, hours=j*2)
                )
                sample_activities.append(activity)
            
            # Profile update activity
            if i < 3:  # Only for first few users
                activity = ActivityLog(
                    user_id=user.id,
                    action='Profile Update',
                    description='User updated profile information',
                    ip_address=f'192.168.1.{20 + i}',
                    timestamp=datetime.utcnow() - timedelta(days=i+2, hours=5)
                )
                sample_activities.append(activity)
            
            # Logout activities
            for j in range(2):
                activity = ActivityLog(
                    user_id=user.id,
                    action='Logout',
                    description='User logged out',
                    ip_address=f'192.168.1.{30 + i + j}',
                    timestamp=datetime.utcnow() - timedelta(days=j+1, hours=j*3+1)
                )
                sample_activities.append(activity)
        
        # Skip failed login attempts for now to avoid NULL constraint issues
        
        for activity in sample_activities:
            db.session.add(activity)
        
        db.session.commit()
        print(f"Created {len(sample_activities)} activity logs successfully!")
        
        # Update last login times for active users
        print("Updating last login times...")
        for user in users:
            if user.is_active:
                user.last_login = datetime.utcnow() - timedelta(days=1)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"Total Users Created: {len(users)}")
        print(f"Admin Users: {len([u for u in users if u.is_admin])}")
        print(f"Active Users: {len([u for u in users if u.is_active])}")
        print(f"Activity Logs: {len(sample_activities)}")
        print("\nADMIN LOGIN CREDENTIALS:")
        print("Email: admin@dashboard.com")
        print("Password: admin123")
        print("\nSample User Credentials:")
        print("Email: alice.smith@email.com")
        print("Password: password123")
        print("="*50)

if __name__ == '__main__':
    seed_database()
