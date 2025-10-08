from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models.user import User
from bson import ObjectId
import re

auth_bp = Blueprint('auth', __name__)

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        """Custom username validation"""
        # Check for valid characters (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', username.data):
            raise ValidationError('Username can only contain letters, numbers, and underscores')
        
        # Check if username already exists
        if User.get_by_username(username.data):
            raise ValidationError('Username is already taken')
    
    def validate_email(self, email):
        """Custom email validation"""
        # Check if email already exists
        if User.get_by_email(email.data):
            raise ValidationError('Email is already registered')

class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('leagues.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            user = User.create(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            
            if user:
                login_user(user, remember=True)
                flash('Registration successful! Welcome to Fantasy Betting League!', 'success')
                return redirect(url_for('leagues.dashboard'))
            else:
                flash('Registration failed. Please try again.', 'error')
                
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('leagues.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            user = User.get_by_email(form.email.data)
            
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                
                if next_page:
                    return redirect(next_page)
                else:
                    flash('Welcome back!', 'success')
                    return redirect(url_for('leagues.dashboard'))
            else:
                flash('Invalid email or password.', 'error')
                
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Get user's leagues with basic stats
    from models.league import League
    user_leagues = League.get_user_leagues(current_user._id)
    
    # Calculate basic stats
    total_leagues = len(user_leagues)
    active_leagues = len([l for l in user_leagues if l.status == 'active'])
    
    return render_template('auth/profile.html', 
                         user=current_user,
                         total_leagues=total_leagues,
                         active_leagues=active_leagues)

@auth_bp.route('/api/check-username')
def check_username():
    """API endpoint to check username availability"""
    username = request.args.get('username')
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    # Check username format
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return jsonify({'available': False, 'message': 'Invalid username format'})
    
    if len(username) < 3 or len(username) > 20:
        return jsonify({'available': False, 'message': 'Username must be 3-20 characters'})
    
    # Check if username exists
    if User.get_by_username(username):
        return jsonify({'available': False, 'message': 'Username is already taken'})
    
    return jsonify({'available': True, 'message': 'Username is available'})

@auth_bp.route('/api/check-email')
def check_email():
    """API endpoint to check email availability"""
    email = request.args.get('email')
    
    if not email:
        return jsonify({'available': False, 'message': 'Email is required'})
    
    # Check if email exists
    if User.get_by_email(email):
        return jsonify({'available': False, 'message': 'Email is already registered'})
    
    return jsonify({'available': True, 'message': 'Email is available'})
