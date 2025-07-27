from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Bet, Ticket, League

bets_bp = Blueprint('bets', __name__)


@bets_bp.route('/place/<ticket_id>', methods=['POST'])
@login_required
def place_bet(ticket_id):
    """Place a bet on a ticket"""
    ticket = Ticket.get_by_id(ticket_id)
    if not ticket:
        flash('Ticket not found', 'error')
        return redirect(url_for('leagues.dashboard'))

    league = League.get_by_id(ticket.league_id)
    if not league or not league.is_member(current_user.get_id()):
        flash('Access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    if not ticket.is_open():
        flash('This ticket is not open for betting', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    # Get form data
    selected_option = request.form.get('selected_option')
    amount = request.form.get('amount')

    if not selected_option or not amount:
        flash('Please select an option and enter an amount', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    try:
        amount = float(amount)
    except ValueError:
        flash('Invalid bet amount', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    # Validate amount
    user_balance = league.get_member_balance(current_user.get_id())
    if amount > user_balance:
        flash('Insufficient balance', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    if amount <= 0:
        flash('Bet amount must be positive', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    # Validate selected option
    valid_options = [opt['option_text'] for opt in ticket.options]
    if selected_option not in valid_options:
        flash('Invalid option selected', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    # Check if user already has a bet on this ticket
    existing_bet = None
    user_bets = Bet.get_user_bets(current_user.get_id(), ticket.league_id)
    for bet in user_bets:
        if bet.ticket_id == str(ticket._id):
            existing_bet = bet
            break

    if existing_bet:
        flash('You already have a bet on this ticket', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    # Create new bet
    bet = Bet(
        user_id=current_user.get_id(),
        league_id=ticket.league_id,
        ticket_id=ticket_id,
        amount=amount,
        selected_option=selected_option
    )

    # Calculate potential payout
    bet.calculate_payout(ticket)
    bet.save()

    # Deduct amount from user's balance
    new_balance = user_balance - amount
    league.update_member_balance(current_user.get_id(), new_balance)

    flash(
        f'Bet placed successfully! Potential payout: ${bet.potential_payout:.2f}', 'success')
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))


@bets_bp.route('/history')
@login_required
def history():
    """User's betting history"""
    user_bets = Bet.get_user_bets(current_user.get_id())
    return render_template('bets/history.html', bets=user_bets)


@bets_bp.route('/league/<league_id>/history')
@login_required
def league_history(league_id):
    """Betting history for a specific league"""
    league = League.get_by_id(league_id)
    if not league or not league.is_member(current_user.get_id()):
        flash('Access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    user_bets = Bet.get_user_bets(current_user.get_id(), league_id)
    return render_template('bets/league_history.html',
                           bets=user_bets,
                           league=league)


@bets_bp.route('/stats')
@login_required
def stats():
    """User's betting statistics"""
    stats = Bet.get_user_stats(current_user.get_id())
    return render_template('bets/stats.html', stats=stats)


@bets_bp.route('/league/<league_id>/stats')
@login_required
def league_stats(league_id):
    """User's betting statistics for a specific league"""
    league = League.get_by_id(league_id)
    if not league or not league.is_member(current_user.get_id()):
        flash('Access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    stats = Bet.get_user_stats(current_user.get_id(), league_id)
    return render_template('bets/league_stats.html',
                           stats=stats,
                           league=league)


@bets_bp.route('/cancel/<bet_id>', methods=['POST'])
@login_required
def cancel_bet(bet_id):
    """Cancel a pending bet (if allowed)"""
    bet = Bet.get_by_id(bet_id)
    if not bet or bet.user_id != current_user.get_id():
        flash('Bet not found or access denied', 'error')
        return redirect(url_for('bets.history'))

    if not bet.is_pending():
        flash('Only pending bets can be cancelled', 'error')
        return redirect(url_for('bets.history'))

    ticket = Ticket.get_by_id(bet.ticket_id)
    if not ticket or not ticket.is_open():
        flash('Cannot cancel bet - ticket is no longer open', 'error')
        return redirect(url_for('bets.history'))

    league = League.get_by_id(bet.league_id)
    if not league:
        flash('League not found', 'error')
        return redirect(url_for('bets.history'))

    # Refund the bet amount
    current_balance = league.get_member_balance(current_user.get_id())
    new_balance = current_balance + bet.amount
    league.update_member_balance(current_user.get_id(), new_balance)

    # Delete the bet
    from models import get_db
    db = get_db()
    db.bets.delete_one({'_id': bet._id})

    flash('Bet cancelled and amount refunded', 'success')
    return redirect(url_for('bets.history'))
