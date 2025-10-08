from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField, DateTimeField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, Length, NumberRange
from models.league import League
from models.ticket import Ticket
from bson import ObjectId
from datetime import datetime, timedelta

tickets_bp = Blueprint('tickets', __name__)

class OptionForm(FlaskForm):
    """Form for betting option"""
    option_text = StringField('Option', validators=[DataRequired(), Length(max=100)])
    odds = FloatField('Odds', validators=[DataRequired(), NumberRange(min=1.01, max=100)])

class CreateTicketForm(FlaskForm):
    """Form for creating a new ticket"""
    title = StringField('Ticket Title', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Title must be between 3 and 100 characters')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=500, message='Description must be less than 500 characters')
    ])
    ticket_type = SelectField('Bet Type', choices=[
        ('moneyline', 'Moneyline'),
        ('over_under', 'Over/Under')
    ], validators=[DataRequired()])
    
    # For over/under bets
    target_value = FloatField('Target Value', validators=[
        NumberRange(min=0.5, max=1000, message='Target value must be between 0.5 and 1000')
    ])
    over_odds = FloatField('Over Odds', validators=[
        NumberRange(min=1.01, max=100, message='Odds must be between 1.01 and 100')
    ])
    under_odds = FloatField('Under Odds', validators=[
        NumberRange(min=1.01, max=100, message='Odds must be between 1.01 and 100')
    ])
    
    # For moneyline bets
    options = FieldList(FormField(OptionForm), min_entries=2, max_entries=10)
    
    closes_at = DateTimeField('Closes At', format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Create Ticket')

@tickets_bp.route('/<league_id>/create', methods=['GET', 'POST'])
@login_required
def create(league_id):
    """Create new ticket (admin only)"""
    try:
        league = League.get_by_id(league_id)
        
        if not league:
            flash('League not found.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Check if user is admin
        if not league.is_admin(current_user._id):
            flash('You do not have permission to create tickets.', 'error')
            return redirect(url_for('leagues.detail', league_id=league_id))
        
        form = CreateTicketForm()
        
        if form.validate_on_submit():
            try:
                ticket = None
                
                if form.ticket_type.data == 'moneyline':
                    # Create moneyline ticket
                    options_data = []
                    for option_form in form.options:
                        if option_form.option_text.data.strip():
                            options_data.append({
                                'option_text': option_form.option_text.data.strip(),
                                'odds': option_form.odds.data
                            })
                    
                    if len(options_data) < 2:
                        flash('Moneyline tickets must have at least 2 options.', 'error')
                        return render_template('tickets/create.html', form=form, league=league)
                    
                    ticket = Ticket.create_moneyline(
                        league_id=league._id,
                        title=form.title.data,
                        description=form.description.data,
                        options=options_data,
                        created_by=current_user._id,
                        closes_at=form.closes_at.data
                    )
                
                elif form.ticket_type.data == 'over_under':
                    # Create over/under ticket
                    ticket = Ticket.create_over_under(
                        league_id=league._id,
                        title=form.title.data,
                        description=form.description.data,
                        target_value=form.target_value.data,
                        over_odds=form.over_odds.data,
                        under_odds=form.under_odds.data,
                        created_by=current_user._id,
                        closes_at=form.closes_at.data
                    )
                
                if ticket:
                    flash(f'Ticket "{ticket.title}" created successfully!', 'success')
                    return redirect(url_for('leagues.detail', league_id=league_id))
                else:
                    flash('Failed to create ticket. Please try again.', 'error')
                    
            except Exception as e:
                flash('An error occurred while creating the ticket.', 'error')
        
        return render_template('tickets/create.html', form=form, league=league)
        
    except Exception as e:
        flash('An error occurred while loading the ticket creation page.', 'error')
        return redirect(url_for('leagues.dashboard'))

@tickets_bp.route('/<ticket_id>')
@login_required
def detail(ticket_id):
    """Ticket detail page"""
    try:
        ticket = Ticket.get_by_id(ticket_id)
        
        if not ticket:
            flash('Ticket not found.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Get league and check membership
        league = League.get_by_id(ticket.league_id)
        
        if not league or not league.get_member(current_user._id):
            flash('You are not a member of this league.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Get user's bet for this ticket
        from models.bet import Bet
        user_bet = Bet.get_user_ticket_bet(current_user._id, ticket._id)
        
        # Get all bets for this ticket (for admin view)
        all_bets = []
        if league.is_admin(current_user._id):
            all_bets = Bet.get_ticket_bets(ticket._id)
        
        return render_template('tickets/detail.html',
                             ticket=ticket,
                             league=league,
                             user_bet=user_bet,
                             all_bets=all_bets)
        
    except Exception as e:
        flash('An error occurred while loading the ticket.', 'error')
        return redirect(url_for('leagues.dashboard'))

@tickets_bp.route('/<ticket_id>/resolve', methods=['POST'])
@login_required
def resolve(ticket_id):
    """Resolve ticket (admin only)"""
    try:
        ticket = Ticket.get_by_id(ticket_id)
        
        if not ticket:
            flash('Ticket not found.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Get league and check admin permissions
        league = League.get_by_id(ticket.league_id)
        
        if not league or not league.is_admin(current_user._id):
            flash('You do not have permission to resolve this ticket.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
        winning_option = request.form.get('winning_option')
        
        if not winning_option:
            flash('Please select a winning option.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
        # Validate winning option
        valid_options = [option['option_text'] for option in ticket.options]
        if winning_option not in valid_options:
            flash('Invalid winning option selected.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
        # Resolve ticket
        if ticket.resolve_ticket(winning_option):
            ticket.save()
            
            # Resolve all bets for this ticket
            from models.bet import Bet
            result = Bet.resolve_bets(ticket._id, winning_option)
            
            # Update user balances
            update_user_balances(ticket, winning_option, league)
            
            flash(f'Ticket resolved! {result["won"]} bets won, {result["lost"]} bets lost.', 'success')
        else:
            flash('Failed to resolve ticket.', 'error')
        
        return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
    except Exception as e:
        flash('An error occurred while resolving the ticket.', 'error')
        return redirect(url_for('leagues.dashboard'))

def update_user_balances(ticket, winning_option, league):
    """Update user balances after ticket resolution"""
    try:
        from models.bet import Bet
        bets = Bet.get_ticket_bets(ticket._id)
        
        for bet in bets:
            user_member = league.get_member(bet.user_id)
            if user_member:
                if bet.selected_option == winning_option:
                    # User won - add winnings to balance
                    new_balance = user_member['balance'] + bet.potential_payout
                    league.update_member_balance(bet.user_id, new_balance)
                # If user lost, balance remains the same (bet amount was already deducted)
        
        league.save()
        
    except Exception as e:
        print(f"Error updating user balances: {e}")

@tickets_bp.route('/<ticket_id>/close', methods=['POST'])
@login_required
def close(ticket_id):
    """Close ticket for new bets (admin only)"""
    try:
        ticket = Ticket.get_by_id(ticket_id)
        
        if not ticket:
            flash('Ticket not found.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Get league and check admin permissions
        league = League.get_by_id(ticket.league_id)
        
        if not league or not league.is_admin(current_user._id):
            flash('You do not have permission to close this ticket.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
        if ticket.close_ticket():
            ticket.save()
            flash('Ticket closed for new bets.', 'success')
        else:
            flash('Failed to close ticket.', 'error')
        
        return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
    except Exception as e:
        flash('An error occurred while closing the ticket.', 'error')
        return redirect(url_for('leagues.dashboard'))

@tickets_bp.route('/api/<league_id>/tickets')
@login_required
def api_tickets(league_id):
    """API endpoint for league tickets"""
    try:
        league = League.get_by_id(league_id)
        
        if not league or not league.get_member(current_user._id):
            return jsonify({'error': 'League not found or access denied'}), 404
        
        tickets = Ticket.get_league_tickets(league._id)
        
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'id': str(ticket._id),
                'title': ticket.title,
                'description': ticket.description,
                'type': ticket.ticket_type,
                'status': ticket.status,
                'created_at': ticket.created_at.isoformat(),
                'closes_at': ticket.closes_at.isoformat() if ticket.closes_at else None,
                'options': ticket.options
            })
        
        return jsonify({
            'league_id': str(league._id),
            'tickets': tickets_data
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch tickets'}), 500
