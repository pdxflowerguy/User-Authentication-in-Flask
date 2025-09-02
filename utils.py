
from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user
from models import ActivityLog
from app import db

def admin_required(f):
    """Decorator to require admin privileges for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        if not current_user.is_admin:
            flash("You need administrator privileges to access this page.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def log_activity(user_id, action, description=None):
    """Log user activity."""
    try:
        # Only log if we have a valid user_id or if it's a system action
        activity = ActivityLog(
            user_id=user_id if user_id else None,
            action=action,
            description=description,
            ip_address=request.environ.get('REMOTE_ADDR')
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error logging activity: {e}")

def get_user_stats():
    """Get user statistics for dashboard."""
    from models import User
    from datetime import datetime, timedelta
    
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    
    # Get users registered in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users = User.query.filter(User.created_at >= thirty_days_ago).count()
    
    # Get users by month for chart (last 12 months)
    user_growth = []
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=1) + timedelta(days=32)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        count = User.query.filter(
            User.created_at >= month_start,
            User.created_at <= month_end
        ).count()
        
        user_growth.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'new_users': new_users,
        'user_growth': list(reversed(user_growth))
    }
