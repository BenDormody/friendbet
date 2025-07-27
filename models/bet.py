from datetime import datetime
from bson import ObjectId
from database import get_db


class Bet:
    def __init__(self, user_id, league_id, ticket_id, amount, selected_option,
                 potential_payout=None, _id=None, status='pending', placed_at=None):
        self.user_id = user_id
        self.league_id = league_id
        self.ticket_id = ticket_id
        self.amount = amount
        self.selected_option = selected_option
        self.potential_payout = potential_payout
        self._id = _id
        self.status = status  # 'pending', 'won', 'lost'
        self.placed_at = placed_at or datetime.utcnow()

    @staticmethod
    def get_by_id(bet_id):
        db = get_db()
        bet_data = db.bets.find_one({'_id': ObjectId(bet_id)})
        if bet_data:
            return Bet._from_dict(bet_data)
        return None

    @staticmethod
    def get_user_bets(user_id, league_id=None):
        db = get_db()
        query = {'user_id': str(user_id)}
        if league_id:
            query['league_id'] = str(league_id)

        bets_data = db.bets.find(query).sort('placed_at', -1)
        return [Bet._from_dict(bet_data) for bet_data in bets_data]

    @staticmethod
    def get_ticket_bets(ticket_id):
        db = get_db()
        bets_data = db.bets.find({'ticket_id': str(ticket_id)})
        return [Bet._from_dict(bet_data) for bet_data in bets_data]

    @staticmethod
    def get_league_bets(league_id):
        db = get_db()
        bets_data = db.bets.find(
            {'league_id': str(league_id)}).sort('placed_at', -1)
        return [Bet._from_dict(bet_data) for bet_data in bets_data]

    def save(self):
        db = get_db()
        if self._id is None:
            # New bet
            bet_data = {
                'user_id': str(self.user_id),
                'league_id': str(self.league_id),
                'ticket_id': str(self.ticket_id),
                'amount': self.amount,
                'selected_option': self.selected_option,
                'potential_payout': self.potential_payout,
                'status': self.status,
                'placed_at': self.placed_at
            }
            result = db.bets.insert_one(bet_data)
            self._id = result.inserted_id
        else:
            # Update existing bet
            db.bets.update_one(
                {'_id': self._id},
                {
                    '$set': {
                        'amount': self.amount,
                        'selected_option': self.selected_option,
                        'potential_payout': self.potential_payout,
                        'status': self.status
                    }
                }
            )
        return self

    def calculate_payout(self, ticket):
        """Calculate potential payout based on ticket odds"""
        odds = ticket.get_option_odds(self.selected_option)
        if odds:
            # For American odds: positive odds = profit, negative odds = amount to bet
            if odds > 0:
                self.potential_payout = self.amount + \
                    (self.amount * odds / 100)
            else:
                self.potential_payout = self.amount + \
                    (self.amount * 100 / abs(odds))
        else:
            self.potential_payout = self.amount
        return self.potential_payout

    def resolve(self, ticket_resolution):
        """Resolve bet based on ticket resolution"""
        if self.selected_option == ticket_resolution:
            self.status = 'won'
        else:
            self.status = 'lost'
        self.save()
        return self.status

    def get_payout_amount(self):
        """Get actual payout amount based on bet status"""
        if self.status == 'won':
            return self.potential_payout
        elif self.status == 'lost':
            return 0
        else:
            return None

    def is_pending(self):
        return self.status == 'pending'

    def is_won(self):
        return self.status == 'won'

    def is_lost(self):
        return self.status == 'lost'

    @staticmethod
    def resolve_ticket_bets(ticket_id, resolution):
        """Resolve all bets for a specific ticket"""
        bets = Bet.get_ticket_bets(ticket_id)
        for bet in bets:
            bet.resolve(resolution)
        return bets

    @staticmethod
    def get_user_stats(user_id, league_id=None):
        """Get betting statistics for a user"""
        bets = Bet.get_user_bets(user_id, league_id)

        total_bets = len(bets)
        won_bets = len([b for b in bets if b.is_won()])
        lost_bets = len([b for b in bets if b.is_lost()])
        pending_bets = len([b for b in bets if b.is_pending()])

        total_wagered = sum(b.amount for b in bets)
        total_won = sum(b.get_payout_amount() or 0 for b in bets if b.is_won())
        net_profit = total_won - total_wagered

        win_rate = (won_bets / total_bets * 100) if total_bets > 0 else 0

        return {
            'total_bets': total_bets,
            'won_bets': won_bets,
            'lost_bets': lost_bets,
            'pending_bets': pending_bets,
            'total_wagered': total_wagered,
            'total_won': total_won,
            'net_profit': net_profit,
            'win_rate': win_rate
        }

    @staticmethod
    def _from_dict(bet_data):
        return Bet(
            user_id=bet_data['user_id'],
            league_id=bet_data['league_id'],
            ticket_id=bet_data['ticket_id'],
            amount=bet_data['amount'],
            selected_option=bet_data['selected_option'],
            potential_payout=bet_data.get('potential_payout'),
            _id=bet_data['_id'],
            status=bet_data.get('status', 'pending'),
            placed_at=bet_data['placed_at']
        )
