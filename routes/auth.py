from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')

        if User.get_by_username(username):
            flash('Username already exists', 'error')
            return render_template('auth/register.html')

        if User.get_by_email(email):
            flash('Email already registered', 'error')
            return render_template('auth/register.html')

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('auth/login.html')

        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('leagues.dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('auth/login.html')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)
