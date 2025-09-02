from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    request,
    jsonify
)

from datetime import timedelta, datetime
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError


from flask_bcrypt import Bcrypt,generate_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import create_app,db,login_manager,bcrypt
from models import User, ActivityLog
from forms import (
    login_form, 
    register_form, 
    profile_form, 
    change_password_form, 
    admin_user_form,
    search_form
)
from utils import admin_required, log_activity, get_user_stats


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)  # Extended session time

@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("index.html", title="Home")


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.pwd, form.pwd.data):
                if user.is_active:
                    login_user(user)
                    # Update last login
                    user.last_login = datetime.utcnow()
                    db.session.commit()
                    log_activity(user.id, "Login", "User logged in successfully")
                    flash(f"Welcome back, {user.username}!", "success")
                    return redirect(url_for('dashboard'))
                else:
                    flash("Your account has been deactivated. Please contact administrator.", "warning")
            else:
                flash("Invalid email or password!", "danger")
                log_activity(None, "Failed Login", f"Failed login attempt for email: {form.email.data}")
        except Exception as e:
            flash("An error occurred during login. Please try again.", "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )


@app.route("/dashboard/")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))


@app.route("/admin/dashboard/")
@login_required
@admin_required
def admin_dashboard():
    stats = get_user_stats()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    
    return render_template("admin/dashboard.html",
                         title="Admin Dashboard",
                         stats=stats,
                         recent_users=recent_users,
                         recent_activities=recent_activities)


@app.route("/user/dashboard/")
@login_required
def user_dashboard():
    user_activities = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    return render_template("user/dashboard.html",
                         title="User Dashboard",
                         activities=user_activities)


@app.route("/admin/users/")
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    role_filter = request.args.get('role', 'all', type=str)
    status_filter = request.args.get('status', 'all', type=str)
    
    query = User.query
    
    # Apply filters
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.first_name.contains(search)) |
            (User.last_name.contains(search))
        )
    
    if role_filter == 'admin':
        query = query.filter_by(is_admin=True)
    elif role_filter == 'user':
        query = query.filter_by(is_admin=False)
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    users = query.paginate(page=page, per_page=10, error_out=False)
    form = search_form()
    form.search.data = search
    form.role.data = role_filter
    form.status.data = status_filter
    
    return render_template("admin/users.html",
                         title="Manage Users",
                         users=users,
                         form=form)



# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            phone = form.phone.data
            
            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                is_admin=False,  # Regular users are not admin by default
                is_active=True
            )
    
            db.session.add(newuser)
            db.session.commit()
            log_activity(newuser.id, "Registration", "New user account created")
            flash(f"Account successfully created! Please log in.", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occurred!", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )


@app.route("/admin/user/<int:user_id>/edit", methods=("GET", "POST"))
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = admin_user_form()
    
    if form.validate_on_submit():
        try:
            # Check if email or username already exists for another user
            existing_email = User.query.filter(User.email == form.email.data, User.id != user_id).first()
            existing_username = User.query.filter(User.username == form.username.data, User.id != user_id).first()
            
            if existing_email:
                flash("Email already exists for another user!", "danger")
            elif existing_username:
                flash("Username already exists for another user!", "danger")
            else:
                user.username = form.username.data
                user.email = form.email.data
                user.first_name = form.first_name.data
                user.last_name = form.last_name.data
                user.phone = form.phone.data
                user.is_admin = form.is_admin.data
                user.is_active = form.is_active.data
                
                db.session.commit()
                log_activity(current_user.id, "User Edit", f"Edited user: {user.username}")
                flash(f"User {user.username} updated successfully!", "success")
                return redirect(url_for('manage_users'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the user.", "danger")
    
    # Populate form with current user data
    form.username.data = user.username
    form.email.data = user.email
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.phone.data = user.phone
    form.is_admin.data = user.is_admin
    form.is_active.data = user.is_active
    
    return render_template("admin/edit_user.html",
                         title=f"Edit User - {user.username}",
                         form=form,
                         user=user)


@app.route("/admin/user/<int:user_id>/delete", methods=("POST",))
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("You cannot delete your own account!", "danger")
    else:
        try:
            username = user.username
            db.session.delete(user)
            db.session.commit()
            log_activity(current_user.id, "User Delete", f"Deleted user: {username}")
            flash(f"User {username} deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while deleting the user.", "danger")
    
    return redirect(url_for('manage_users'))


@app.route("/profile/", methods=("GET", "POST"))
@login_required
def profile():
    form = profile_form()
    
    if form.validate_on_submit():
        try:
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.phone = form.phone.data
            
            db.session.commit()
            log_activity(current_user.id, "Profile Update", "User updated profile information")
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating your profile.", "danger")
    
    # Populate form with current user data
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.phone.data = current_user.phone
    
    return render_template("user/profile.html",
                         title="My Profile",
                         form=form)


@app.route("/change-password/", methods=("GET", "POST"))
@login_required
def change_password():
    form = change_password_form()
    
    if form.validate_on_submit():
        try:
            if bcrypt.check_password_hash(current_user.pwd, form.current_pwd.data):
                current_user.pwd = bcrypt.generate_password_hash(form.new_pwd.data)
                db.session.commit()
                log_activity(current_user.id, "Password Change", "User changed password")
                flash("Password changed successfully!", "success")
                return redirect(url_for('profile'))
            else:
                flash("Current password is incorrect!", "danger")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while changing password.", "danger")
    
    return render_template("user/change_password.html",
                         title="Change Password",
                         form=form)

@app.route("/admin/activities/")
@login_required
@admin_required
def activity_logs():
    page = request.args.get('page', 1, type=int)
    activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template("admin/activities.html",
                         title="Activity Logs",
                         activities=activities)


@app.route("/api/stats")
@login_required
@admin_required
def api_stats():
    stats = get_user_stats()
    return jsonify(stats)


@app.route("/logout")
@login_required
def logout():
    log_activity(current_user.id, "Logout", "User logged out")
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
