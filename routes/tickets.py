from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Ticket, League, Bet

tickets_bp = Blueprint('tickets', __name__)


@tickets_bp.route('/league/<league_id>')
@login_required
def list_tickets(league_id):
    """List all tickets for a league"""
    league = League.get_by_id(league_id)
    if not league or not league.is_member(current_user.get_id()):
        flash('League not found or access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    tickets = Ticket.get_league_tickets(league_id)
    return render_template('tickets/list.html',
                           league=league,
                           tickets=tickets,
                           is_admin=league.is_admin(current_user.get_id()))


@tickets_bp.route('/league/<league_id>/create', methods=['GET', 'POST'])
@login_required
def create_ticket(league_id):
    """Create a new ticket (admin only)"""
    league = League.get_by_id(league_id)
    if not league or not league.is_admin(current_user.get_id()):
        flash('Access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        ticket_type = request.form.get('type')

        if not title or not ticket_type:
            flash('Title and type are required', 'error')
            return render_template('tickets/create.html', league=league)

        # Create ticket
        ticket = Ticket(
            league_id=league_id,
            title=title,
            description=description,
            ticket_type=ticket_type,
            created_by=current_user.get_id()
        )

        # Add options based on ticket type
        if ticket_type == 'moneyline':
            options = []
            for i in range(1, 6):  # Allow up to 5 options
                option_text = request.form.get(f'option_{i}')
                odds = request.form.get(f'odds_{i}')
                if option_text and odds:
                    try:
                        odds = float(odds)
                        options.append({
                            'option_text': option_text,
                            'odds': odds
                        })
                    except ValueError:
                        flash(f'Invalid odds for option {i}', 'error')
                        return render_template('tickets/create.html', league=league)

            if len(options) < 2:
                flash('At least 2 options are required for moneyline bets', 'error')
                return render_template('tickets/create.html', league=league)

            ticket.options = options

        elif ticket_type == 'over_under':
            target_value = request.form.get('target_value')
            over_odds = request.form.get('over_odds')
            under_odds = request.form.get('under_odds')

            if not target_value or not over_odds or not under_odds:
                flash('Target value and odds are required for over/under bets', 'error')
                return render_template('tickets/create.html', league=league)

            try:
                target_value = float(target_value)
                over_odds = float(over_odds)
                under_odds = float(under_odds)
            except ValueError:
                flash('Invalid numeric values', 'error')
                return render_template('tickets/create.html', league=league)

            ticket.target_value = target_value
            ticket.options = [
                {'option_text': f'Over {target_value}', 'odds': over_odds},
                {'option_text': f'Under {target_value}', 'odds': under_odds}
            ]

        ticket.save()
        flash('Ticket created successfully!', 'success')
        return redirect(url_for('tickets.list_tickets', league_id=league_id))

    return render_template('tickets/create.html', league=league)


@tickets_bp.route('/<ticket_id>')
@login_required
def view_ticket(ticket_id):
    """View ticket details and place bets"""
    ticket = Ticket.get_by_id(ticket_id)
    if not ticket:
        flash('Ticket not found', 'error')
        return redirect(url_for('leagues.dashboard'))

    league = League.get_by_id(ticket.league_id)
    if not league or not league.is_member(current_user.get_id()):
        flash('Access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    # Get user's balance
    user_balance = league.get_member_balance(current_user.get_id())

    # Get existing bet by user
    existing_bet = None
    if ticket.is_open():
        user_bets = Bet.get_user_bets(current_user.get_id(), ticket.league_id)
        for bet in user_bets:
            if bet.ticket_id == str(ticket._id):
                existing_bet = bet
                break

    return render_template('tickets/view.html',
                           ticket=ticket,
                           league=league,
                           user_balance=user_balance,
                           existing_bet=existing_bet,
                           is_admin=league.is_admin(current_user.get_id()))


@tickets_bp.route('/<ticket_id>/resolve', methods=['POST'])
@login_required
def resolve_ticket(ticket_id):
    """Resolve a ticket (admin only)"""
    ticket = Ticket.get_by_id(ticket_id)
    if not ticket:
        flash('Ticket not found', 'error')
        return redirect(url_for('leagues.dashboard'))

    league = League.get_by_id(ticket.league_id)
    if not league or not league.is_admin(current_user.get_id()):
        flash('Access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    if not ticket.is_open():
        flash('Ticket is already resolved or closed', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    resolution = request.form.get('resolution')
    if not resolution:
        flash('Resolution is required', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    # Validate resolution
    valid_options = [opt['option_text'] for opt in ticket.options]
    if resolution not in valid_options:
        flash('Invalid resolution', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    # Resolve ticket and all bets
    ticket.resolve(resolution)
    Bet.resolve_ticket_bets(str(ticket._id), resolution)

    # Update user balances
    bets = Bet.get_ticket_bets(str(ticket._id))
    for bet in bets:
        if bet.is_won():
            # Add winnings to user's balance
            current_balance = league.get_member_balance(bet.user_id)
            new_balance = current_balance + bet.get_payout_amount()
            league.update_member_balance(bet.user_id, new_balance)

    flash('Ticket resolved successfully!', 'success')
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))


@tickets_bp.route('/<ticket_id>/close', methods=['POST'])
@login_required
def close_ticket(ticket_id):
    """Close a ticket (admin only)"""
    ticket = Ticket.get_by_id(ticket_id)
    if not ticket:
        flash('Ticket not found', 'error')
        return redirect(url_for('leagues.dashboard'))

    league = League.get_by_id(ticket.league_id)
    if not league or not league.is_admin(current_user.get_id()):
        flash('Access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    if not ticket.is_open():
        flash('Ticket is already closed or resolved', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

    ticket.close()
    flash('Ticket closed successfully!', 'success')
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
