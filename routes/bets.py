from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from models.league import League
from models.ticket import Ticket
from models.bet import Bet
from bson import ObjectId

bets_bp = Blueprint('bets', __name__)

class PlaceBetForm(FlaskForm):
    """Form for placing a bet"""
    amount = FloatField('Bet Amount', validators=[
        DataRequired(),
        NumberRange(min=1, max=10000, message='Bet amount must be between $1 and $10,000')
    ])
    selected_option = StringField('Selected Option', validators=[DataRequired()])
    submit = SubmitField('Place Bet')

@bets_bp.route('/<ticket_id>/place', methods=['POST'])
@login_required
def place_bet(ticket_id):
    """Place a bet on a ticket"""
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
        
        # Check if ticket is open for betting
        if not ticket.can_place_bets():
            flash('This ticket is no longer accepting bets.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
        # Get form data
        amount = float(request.form.get('amount', 0))
        selected_option = request.form.get('selected_option', '').strip()
        
        # Validate bet amount
        user_member = league.get_member(current_user._id)
        user_balance = user_member['balance']
        
        if amount <= 0:
            flash('Bet amount must be greater than zero.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
        if amount > user_balance:
            flash(f'Insufficient balance. You have ${user_balance:.2f} available.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
        # Validate selected option
        valid_options = [option['option_text'] for option in ticket.options]
        if selected_option not in valid_options:
            flash('Invalid option selected.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
        # Check if user already has a bet on this ticket
        existing_bet = Bet.get_user_ticket_bet(current_user._id, ticket._id)
        if existing_bet:
            flash('You already have a bet on this ticket.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
        # Get odds for selected option
        option_odds = None
        for option in ticket.options:
            if option['option_text'] == selected_option:
                option_odds = option['odds']
                break
        
        if not option_odds:
            flash('Invalid odds for selected option.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
        # Create bet
        bet = Bet.create_bet(
            user_id=current_user._id,
            league_id=league._id,
            ticket_id=ticket._id,
            amount=amount,
            selected_option=selected_option,
            odds=option_odds
        )
        
        if bet:
            # Deduct bet amount from user's balance
            new_balance = user_balance - amount
            league.update_member_balance(current_user._id, new_balance)
            league.save()
            
            flash(f'Bet placed successfully! Potential payout: ${bet.potential_payout:.2f}', 'success')
        else:
            flash('Failed to place bet. Please try again.', 'error')
        
        return redirect(url_for('tickets.detail', ticket_id=ticket_id))
        
    except ValueError as e:
        flash('Invalid bet amount.', 'error')
        return redirect(url_for('tickets.detail', ticket_id=ticket_id))
    except Exception as e:
        flash('An error occurred while placing the bet.', 'error')
        return redirect(url_for('tickets.detail', ticket_id=ticket_id))

@bets_bp.route('/<bet_id>/cancel', methods=['POST'])
@login_required
def cancel_bet(bet_id):
    """Cancel a pending bet"""
    try:
        bet = Bet.get_by_id(bet_id)
        
        if not bet:
            flash('Bet not found.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Check if user owns this bet
        if bet.user_id != current_user._id:
            flash('You can only cancel your own bets.', 'error')
            return redirect(url_for('leagues.dashboard'))
        
        # Check if bet is still pending
        if not bet.is_pending():
            flash('Only pending bets can be cancelled.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=str(bet.ticket_id)))
        
        # Get ticket and check if it's still open
        ticket = Ticket.get_by_id(str(bet.ticket_id))
        if not ticket or not ticket.can_place_bets():
            flash('Cannot cancel bet - ticket is no longer accepting bets.', 'error')
            return redirect(url_for('tickets.detail', ticket_id=str(bet.ticket_id)))
        
        # Get league and refund bet amount
        league = League.get_by_id(bet.league_id)
        if league:
            user_member = league.get_member(current_user._id)
            if user_member:
                new_balance = user_member['balance'] + bet.amount
                league.update_member_balance(current_user._id, new_balance)
                league.save()
        
        # Delete bet
        from database import get_db
        db = get_db()
        db.get_collection('bets').delete_one({'_id': bet._id})
        
        flash('Bet cancelled successfully. Amount refunded to your balance.', 'success')
        return redirect(url_for('tickets.detail', ticket_id=str(bet.ticket_id)))
        
    except Exception as e:
        flash('An error occurred while cancelling the bet.', 'error')
        return redirect(url_for('leagues.dashboard'))

@bets_bp.route('/history')
@login_required
def history():
    """User's betting history"""
    try:
        league_id = request.args.get('league_id')
        
        if league_id:
            # Get bets for specific league
            league = League.get_by_id(league_id)
            if not league or not league.get_member(current_user._id):
                flash('League not found or access denied.', 'error')
                return redirect(url_for('leagues.dashboard'))
            
            bets = Bet.get_user_bets(current_user._id, league._id)
            league_name = league.name
        else:
            # Get all user bets
            bets = Bet.get_user_bets(current_user._id)
            league_name = None
        
        # Get user stats
        user_stats = Bet.get_user_stats(current_user._id, league_id and ObjectId(league_id))
        
        return render_template('bets/history.html',
                             bets=bets,
                             user_stats=user_stats,
                             league_name=league_name)
        
    except Exception as e:
        flash('An error occurred while loading betting history.', 'error')
        return redirect(url_for('leagues.dashboard'))

@bets_bp.route('/api/<league_id>/user-stats')
@login_required
def api_user_stats(league_id):
    """API endpoint for user betting stats"""
    try:
        league = League.get_by_id(league_id)
        
        if not league or not league.get_member(current_user._id):
            return jsonify({'error': 'League not found or access denied'}), 404
        
        user_stats = Bet.get_user_stats(current_user._id, league._id)
        
        return jsonify({
            'league_id': str(league._id),
            'user_id': str(current_user._id),
            'stats': user_stats
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user stats'}), 500

@bets_bp.route('/api/<ticket_id>/user-bet')
@login_required
def api_user_bet(ticket_id):
    """API endpoint for user's bet on a specific ticket"""
    try:
        ticket = Ticket.get_by_id(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Get league and check membership
        league = League.get_by_id(ticket.league_id)
        
        if not league or not league.get_member(current_user._id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Get user's bet
        user_bet = Bet.get_user_ticket_bet(current_user._id, ticket._id)
        
        if user_bet:
            return jsonify({
                'ticket_id': str(ticket._id),
                'bet': {
                    'id': str(user_bet._id),
                    'amount': user_bet.amount,
                    'selected_option': user_bet.selected_option,
                    'potential_payout': user_bet.potential_payout,
                    'status': user_bet.status,
                    'placed_at': user_bet.placed_at.isoformat()
                }
            })
        else:
            return jsonify({
                'ticket_id': str(ticket._id),
                'bet': None
            })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user bet'}), 500

@bets_bp.route('/api/<league_id>/recent-bets')
@login_required
def api_recent_bets(league_id):
    """API endpoint for recent bets in a league"""
    try:
        league = League.get_by_id(league_id)
        
        if not league or not league.get_member(current_user._id):
            return jsonify({'error': 'League not found or access denied'}), 404
        
        # Get recent bets (last 10)
        from database import get_db
        db = get_db()
        
        bets_data = db.get_collection('bets').find({
            'league_id': league._id
        }).sort('placed_at', -1).limit(10)
        
        recent_bets = []
        for bet_data in bets_data:
            recent_bets.append({
                'id': str(bet_data['_id']),
                'user_id': str(bet_data['user_id']),
                'amount': bet_data['amount'],
                'selected_option': bet_data['selected_option'],
                'status': bet_data['status'],
                'placed_at': bet_data['placed_at'].isoformat()
            })
        
        return jsonify({
            'league_id': str(league._id),
            'recent_bets': recent_bets
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch recent bets'}), 500
