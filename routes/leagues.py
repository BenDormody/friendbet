from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Length, NumberRange
from models.league import League
from models.user import User
from models.ticket import Ticket
from models.bet import Bet
from bson import ObjectId
from datetime import datetime, timedelta

leagues_bp = Blueprint('leagues', __name__)

class CreateLeagueForm(FlaskForm):
    """Form for creating a new league"""
    name = StringField('League Name', validators=[
        DataRequired(),
        Length(min=3, max=50, message='League name must be between 3 and 50 characters')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=500, message='Description must be less than 500 characters')
    ])
    starting_balance = FloatField('Starting Balance', validators=[
        DataRequired(),
        NumberRange(min=100, max=10000, message='Starting balance must be between $100 and $10,000')
    ])
    end_date = DateTimeField('End Date (Optional)', format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Create League')

class JoinLeagueForm(FlaskForm):
    """Form for joining a league"""
    invite_code = StringField('Invite Code', validators=[
        DataRequired(),
        Length(min=8, max=8, message='Invite code must be 8 characters')
    ])
    submit = SubmitField('Join League')

@leagues_bp.route('/')
@login_required
def dashboard():
    """User's leagues dashboard"""
    user_leagues = League.get_user_leagues(current_user._id)
    
    # Get basic stats
    total_leagues = len(user_leagues)
    active_leagues = len([l for l in user_leagues if l.status == 'active'])
    
    return render_template('leagues/dashboard.html', 
                         leagues=user_leagues,
                         total_leagues=total_leagues,
                         active_leagues=active_leagues)

@leagues_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new league"""
    form = CreateLeagueForm()
    
    if form.validate_on_submit():
        try:
            league = League.create(
                name=form.name.data,
                description=form.description.data,
                creator_id=current_user._id,
                starting_balance=form.starting_balance.data
            )
            
            if league:
                # Add creator as first member
                league.add_member(current_user._id, current_user.username)
                league.save()
                
                # Add league to user's leagues list
                current_user.add_league(league._id)
                
                flash(f'League "{league.name}" created successfully!', 'success')
                return redirect(url_for('leagues.detail', league_id=str(league._id)))
            else:
                flash('Failed to create league. Please try again.', 'error')
                
        except Exception as e:
            flash('An error occurred while creating the league.', 'error')
    
    return render_template('leagues/create.html', form=form)

@leagues_bp.route('/join', methods=['GET', 'POST'])
@login_required
def join():
    """Join league with invite code"""
    form = JoinLeagueForm()
    
    if form.validate_on_submit():
        try:
            league = League.get_by_invite_code(form.invite_code.data.upper())
            
            if league:
                # Check if user is already a member
                if league.get_member(current_user._id):
                    flash('You are already a member of this league.', 'warning')
                elif league.status != 'active':
                    flash('This league is not accepting new members.', 'error')
                else:
                    # Add user to league
                    if league.add_member(current_user._id, current_user.username):
                        league.save()
                        current_user.add_league(league._id)
                        
                        flash(f'Successfully joined "{league.name}"!', 'success')
                        return redirect(url_for('leagues.detail', league_id=str(league._id)))
                    else:
                        flash('Failed to join league. Please try again.', 'error')
            else:
                flash('Invalid invite code. Please check and try again.', 'error')
                
        except Exception as e:
            flash('An error occurred while joining the league.', 'error')
    
    return render_template('leagues/join.html', form=form)

@leagues_bp.route('/<league_id>')
@login_required
def detail(league_id):
    """League detail page"""
    try:
        league = League.get_by_id(league_id)
        
        if not league:
            flash('League not found.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Check if user is a member
        user_member = league.get_member(current_user._id)
        if not user_member:
            flash('You are not a member of this league.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Get league tickets
        tickets = Ticket.get_league_tickets(league._id)
        
        # Get user's bets for this league
        user_bets = Bet.get_user_bets(current_user._id, league._id)
        
        # Get user stats
        user_stats = Bet.get_user_stats(current_user._id, league._id)
        
        # Get leaderboard
        leaderboard = league.get_leaderboard()
        
        return render_template('leagues/detail.html',
                             league=league,
                             tickets=tickets,
                             user_bets=user_bets,
                             user_stats=user_stats,
                             leaderboard=leaderboard,
                             user_member=user_member)
        
    except Exception as e:
        flash('An error occurred while loading the league.', 'error')
        return redirect(url_for('leagues.dashboard'))

@leagues_bp.route('/<league_id>/leave', methods=['POST'])
@login_required
def leave(league_id):
    """Leave a league"""
    try:
        league = League.get_by_id(league_id)
        
        if not league:
            flash('League not found.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Check if user is a member
        if not league.get_member(current_user._id):
            flash('You are not a member of this league.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Check if user is the creator
        if league.creator_id == current_user._id:
            flash('League creators cannot leave their own league.', 'error')
            return redirect(url_for('leagues.detail', league_id=league_id))
        
        # Remove user from league
        if league.remove_member(current_user._id):
            league.save()
            current_user.remove_league(league._id)
            flash(f'You have left "{league.name}".', 'success')
        else:
            flash('Failed to leave league. Please try again.', 'error')
        
        return redirect(url_for('leagues.dashboard'))
        
    except Exception as e:
        flash('An error occurred while leaving the league.', 'error')
        return redirect(url_for('leagues.dashboard'))

@leagues_bp.route('/<league_id>/settings', methods=['GET', 'POST'])
@login_required
def settings(league_id):
    """League settings page (admin only)"""
    try:
        league = League.get_by_id(league_id)
        
        if not league:
            flash('League not found.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Check if user is admin
        if not league.is_admin(current_user._id):
            flash('You do not have permission to access league settings.', 'error')
            return redirect(url_for('leagues.detail', league_id=league_id))
        
        form = CreateLeagueForm(obj=league)
        
        if form.validate_on_submit():
            league.name = form.name.data
            league.description = form.description.data
            league.starting_balance = form.starting_balance.data
            league.end_date = form.end_date.data
            
            if league.save():
                flash('League settings updated successfully!', 'success')
                return redirect(url_for('leagues.detail', league_id=league_id))
            else:
                flash('Failed to update league settings.', 'error')
        
        return render_template('leagues/settings.html', league=league, form=form)
        
    except Exception as e:
        flash('An error occurred while loading league settings.', 'error')
        return redirect(url_for('leagues.dashboard'))

@leagues_bp.route('/<league_id>/leaderboard')
@login_required
def leaderboard(league_id):
    """League leaderboard page"""
    try:
        league = League.get_by_id(league_id)
        
        if not league:
            flash('League not found.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Check if user is a member
        if not league.get_member(current_user._id):
            flash('You are not a member of this league.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        leaderboard_data = league.get_leaderboard()
        
        return render_template('leagues/leaderboard.html', 
                             league=league, 
                             leaderboard=leaderboard_data)
        
    except Exception as e:
        flash('An error occurred while loading the leaderboard.', 'error')
        return redirect(url_for('leagues.dashboard'))

@leagues_bp.route('/api/<league_id>/leaderboard')
@login_required
def api_leaderboard(league_id):
    """API endpoint for leaderboard data"""
    try:
        league = League.get_by_id(league_id)
        
        if not league or not league.get_member(current_user._id):
            return jsonify({'error': 'League not found or access denied'}), 404
        
        leaderboard_data = league.get_leaderboard()
        
        return jsonify({
            'league_id': str(league._id),
            'league_name': league.name,
            'leaderboard': leaderboard_data
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch leaderboard'}), 500

@leagues_bp.route('/api/join/<invite_code>', methods=['POST'])
@login_required
def api_join(invite_code):
    """API endpoint for joining league"""
    try:
        league = League.get_by_invite_code(invite_code.upper())
        
        if not league:
            return jsonify({'error': 'Invalid invite code'}), 400
        
        if league.get_member(current_user._id):
            return jsonify({'error': 'Already a member of this league'}), 400
        
        if league.status != 'active':
            return jsonify({'error': 'League is not accepting new members'}), 400
        
        # Add user to league
        if league.add_member(current_user._id, current_user.username):
            league.save()
            current_user.add_league(league._id)
            
            return jsonify({
                'success': True,
                'league_id': str(league._id),
                'league_name': league.name
            })
        else:
            return jsonify({'error': 'Failed to join league'}), 500
        
    except Exception as e:
        return jsonify({'error': 'Failed to join league'}), 500
