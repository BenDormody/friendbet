from datetime import datetime
from bson import ObjectId
from database import get_db


class Ticket:
    def __init__(self, league_id, title, description, ticket_type, options=None,
                 target_value=None, _id=None, status='open', resolution=None,
                 created_by=None, created_at=None, closes_at=None, resolved_at=None):
        self.league_id = league_id
        self.title = title
        self.description = description
        self.ticket_type = ticket_type  # 'moneyline' or 'over_under'
        self.options = options or []
        self.target_value = target_value
        self._id = _id
        self.status = status  # 'open', 'closed', 'resolved'
        self.resolution = resolution
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.closes_at = closes_at
        self.resolved_at = resolved_at

    @staticmethod
    def get_by_id(ticket_id):
        db = get_db()
        ticket_data = db.tickets.find_one({'_id': ObjectId(ticket_id)})
        if ticket_data:
            return Ticket._from_dict(ticket_data)
        return None

    @staticmethod
    def get_league_tickets(league_id, status=None):
        db = get_db()
        query = {'league_id': str(league_id)}
        if status:
            query['status'] = status

        tickets_data = db.tickets.find(query).sort('created_at', -1)
        return [Ticket._from_dict(ticket_data) for ticket_data in tickets_data]

    @staticmethod
    def get_open_tickets(league_id):
        return Ticket.get_league_tickets(league_id, 'open')

    def save(self):
        db = get_db()
        if self._id is None:
            # New ticket
            ticket_data = {
                'league_id': str(self.league_id),
                'title': self.title,
                'description': self.description,
                'type': self.ticket_type,
                'options': self.options,
                'target_value': self.target_value,
                'status': self.status,
                'resolution': self.resolution,
                'created_by': str(self.created_by) if self.created_by else None,
                'created_at': self.created_at,
                'closes_at': self.closes_at,
                'resolved_at': self.resolved_at
            }
            result = db.tickets.insert_one(ticket_data)
            self._id = result.inserted_id
        else:
            # Update existing ticket
            db.tickets.update_one(
                {'_id': self._id},
                {
                    '$set': {
                        'title': self.title,
                        'description': self.description,
                        'type': self.ticket_type,
                        'options': self.options,
                        'target_value': self.target_value,
                        'status': self.status,
                        'resolution': self.resolution,
                        'closes_at': self.closes_at,
                        'resolved_at': self.resolved_at
                    }
                }
            )
        return self

    def close(self):
        self.status = 'closed'
        self.save()

    def resolve(self, resolution):
        self.status = 'resolved'
        self.resolution = resolution
        self.resolved_at = datetime.utcnow()
        self.save()

    def is_open(self):
        return self.status == 'open'

    def is_closed(self):
        return self.status == 'closed'

    def is_resolved(self):
        return self.status == 'resolved'

    def get_option_odds(self, option_text):
        for option in self.options:
            if option['option_text'] == option_text:
                return option['odds']
        return None

    def add_option(self, option_text, odds):
        self.options.append({
            'option_text': option_text,
            'odds': odds
        })
        self.save()

    def remove_option(self, option_text):
        self.options = [
            opt for opt in self.options if opt['option_text'] != option_text]
        self.save()

    def get_total_bet_amount(self):
        from .bet import Bet
        bets = Bet.get_ticket_bets(str(self._id))
        return sum(bet.amount for bet in bets)

    def get_bet_counts(self):
        from .bet import Bet
        bets = Bet.get_ticket_bets(str(self._id))
        counts = {}
        for bet in bets:
            option = bet.selected_option
            counts[option] = counts.get(option, 0) + 1
        return counts

    @staticmethod
    def _from_dict(ticket_data):
        return Ticket(
            league_id=ticket_data['league_id'],
            title=ticket_data['title'],
            description=ticket_data['description'],
            ticket_type=ticket_data['type'],
            options=ticket_data.get('options', []),
            target_value=ticket_data.get('target_value'),
            _id=ticket_data['_id'],
            status=ticket_data.get('status', 'open'),
            resolution=ticket_data.get('resolution'),
            created_by=ticket_data.get('created_by'),
            created_at=ticket_data['created_at'],
            closes_at=ticket_data.get('closes_at'),
            resolved_at=ticket_data.get('resolved_at')
        )
