from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import League, User

leagues_bp = Blueprint('leagues', __name__)


@leagues_bp.route('/')
@login_required
def dashboard():
    """User's league dashboard"""
    user_leagues = League.get_user_leagues(current_user.get_id())
    return render_template('leagues/dashboard.html', leagues=user_leagues)


@leagues_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        starting_balance = int(request.form.get('starting_balance', 1000))

        if not name:
            flash('League name is required', 'error')
            return render_template('leagues/create.html')

        # Create new league
        league = League(
            name=name,
            description=description,
            creator_id=current_user.get_id(),
            starting_balance=starting_balance
        )
        league.save()

        # Add creator as member
        league.add_member(current_user.get_id(), starting_balance)

        flash('League created successfully!', 'success')
        return redirect(url_for('leagues.detail', league_id=league._id))

    return render_template('leagues/create.html')


@leagues_bp.route('/<league_id>')
@login_required
def detail(league_id):
    """League detail page"""
    league = League.get_by_id(league_id)
    if not league:
        flash('League not found', 'error')
        return redirect(url_for('leagues.dashboard'))

    if not league.is_member(current_user.get_id()):
        flash('You are not a member of this league', 'error')
        return redirect(url_for('leagues.dashboard'))

    # Get user's balance in this league
    user_balance = league.get_member_balance(current_user.get_id())

    return render_template('leagues/detail.html',
                           league=league,
                           user_balance=user_balance,
                           is_admin=league.is_admin(current_user.get_id()))


@leagues_bp.route('/join', methods=['POST'])
@login_required
def join_by_code():
    """Join a league using invite code"""
    invite_code = request.form.get('invite_code')

    if not invite_code:
        flash('Invite code is required', 'error')
        return redirect(url_for('leagues.dashboard'))

    league = League.get_by_invite_code(invite_code)
    if not league:
        flash('Invalid invite code', 'error')
        return redirect(url_for('leagues.dashboard'))

    if league.is_member(current_user.get_id()):
        flash('You are already a member of this league', 'info')
        return redirect(url_for('leagues.detail', league_id=league._id))

    # Add user to league
    if league.add_member(current_user.get_id()):
        flash('Successfully joined the league!', 'success')
        return redirect(url_for('leagues.detail', league_id=league._id))
    else:
        flash('Failed to join league', 'error')
        return redirect(url_for('leagues.dashboard'))


@leagues_bp.route('/<league_id>/join', methods=['POST'])
@login_required
def join(league_id):
    """Join a league using invite code (legacy route)"""
    invite_code = request.form.get('invite_code')

    if not invite_code:
        flash('Invite code is required', 'error')
        return redirect(url_for('leagues.dashboard'))

    league = League.get_by_invite_code(invite_code)
    if not league:
        flash('Invalid invite code', 'error')
        return redirect(url_for('leagues.dashboard'))

    if league.is_member(current_user.get_id()):
        flash('You are already a member of this league', 'info')
        return redirect(url_for('leagues.detail', league_id=league._id))

    # Add user to league
    if league.add_member(current_user.get_id()):
        flash('Successfully joined the league!', 'success')
        return redirect(url_for('leagues.detail', league_id=league._id))
    else:
        flash('Failed to join league', 'error')
        return redirect(url_for('leagues.dashboard'))


@leagues_bp.route('/<league_id>/members')
@login_required
def members(league_id):
    """League members page"""
    league = League.get_by_id(league_id)
    if not league or not league.is_member(current_user.get_id()):
        flash('League not found or access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    leaderboard = league.get_leaderboard()
    return render_template('leagues/members.html',
                           league=league,
                           leaderboard=leaderboard,
                           is_admin=league.is_admin(current_user.get_id()))


@leagues_bp.route('/<league_id>/settings', methods=['GET', 'POST'])
@login_required
def settings(league_id):
    """League settings (admin only)"""
    league = League.get_by_id(league_id)
    if not league or not league.is_admin(current_user.get_id()):
        flash('Access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        status = request.form.get('status')

        if name:
            league.name = name
        if description is not None:
            league.description = description
        if status:
            league.status = status

        league.save()
        flash('League settings updated', 'success')
        return redirect(url_for('leagues.detail', league_id=league._id))

    return render_template('leagues/settings.html', league=league)


@leagues_bp.route('/<league_id>/invite')
@login_required
def invite(league_id):
    """Generate invite link"""
    league = League.get_by_id(league_id)
    if not league or not league.is_admin(current_user.get_id()):
        flash('Access denied', 'error')
        return redirect(url_for('leagues.dashboard'))

    invite_url = url_for('leagues.join', league_id=league._id, _external=True)
    return render_template('leagues/invite.html',
                           league=league,
                           invite_url=invite_url,
                           invite_code=league.invite_code)
