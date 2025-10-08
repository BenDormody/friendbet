from bson import ObjectId
from datetime import datetime, timedelta
from database import get_db
from typing import Optional, List, Dict, Any


class Ticket:
    """Ticket model for managing betting tickets"""

    def __init__(self, league_id: ObjectId = None, title: str = None, description: str = None,
                 ticket_type: str = 'moneyline', options: List[Dict] = None,
                 target_value: float = None, status: str = 'open',
                 resolution: str = None, created_by: ObjectId = None,
                 created_at: datetime = None, closes_at: datetime = None,
                 resolved_at: datetime = None, _id: ObjectId = None):
        self.league_id = league_id
        self.title = title
        self.description = description
        self.ticket_type = ticket_type  # 'moneyline' or 'over_under'
        self.options = options or []
        self.target_value = target_value  # For over/under bets
        self.status = status  # 'open', 'closed', 'resolved'
        self.resolution = resolution
        self.created_by = created_by
        self.created_at = created_at or datetime.now(datetime.timezone.utc)
        self.closes_at = closes_at
        self.resolved_at = resolved_at
        self._id = _id

    def add_option(self, option_text: str, odds: float) -> bool:
        """Add betting option to ticket"""
        # Check if option already exists
        for option in self.options:
            if option['option_text'] == option_text:
                return False

        option_data = {
            'option_text': option_text,
            'odds': odds
        }
        self.options.append(option_data)
        return True

    def remove_option(self, option_text: str) -> bool:
        """Remove betting option from ticket"""
        for i, option in enumerate(self.options):
            if option['option_text'] == option_text:
                del self.options[i]
                return True
        return False

    def get_option(self, option_text: str) -> Optional[Dict[str, Any]]:
        """Get option data by text"""
        for option in self.options:
            if option['option_text'] == option_text:
                return option
        return None

    def update_option_odds(self, option_text: str, new_odds: float) -> bool:
        """Update odds for specific option"""
        for option in self.options:
            if option['option_text'] == option_text:
                option['odds'] = new_odds
                return True
        return False

    def close_ticket(self) -> bool:
        """Close ticket for new bets"""
        if self.status == 'open':
            self.status = 'closed'
            return True
        return False

    def resolve_ticket(self, winning_option: str) -> bool:
        """Resolve ticket with winning option"""
        if self.status in ['open', 'closed']:
            self.status = 'resolved'
            self.resolution = winning_option
            self.resolved_at = datetime.utcnow()
            return True
        return False

    def is_expired(self) -> bool:
        """Check if ticket is past its closing time"""
        if self.closes_at:
            return datetime.utcnow() > self.closes_at
        return False

    def can_place_bets(self) -> bool:
        """Check if users can still place bets"""
        return self.status == 'open' and not self.is_expired()

    def save(self) -> ObjectId:
        """Save ticket to database"""
        db = get_db()
        ticket_data = {
            'league_id': self.league_id,
            'title': self.title,
            'description': self.description,
            'type': self.ticket_type,
            'options': self.options,
            'target_value': self.target_value,
            'status': self.status,
            'resolution': self.resolution,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'closes_at': self.closes_at,
            'resolved_at': self.resolved_at
        }

        if self._id:
            # Update existing ticket
            result = db.get_collection('tickets').update_one(
                {'_id': self._id},
                {'$set': ticket_data}
            )
            return self._id if result.modified_count > 0 else None
        else:
            # Create new ticket
            result = db.get_collection('tickets').insert_one(ticket_data)
            self._id = result.inserted_id
            return self._id

    def to_dict(self) -> Dict[str, Any]:
        """Convert ticket to dictionary"""
        return {
            '_id': self._id,
            'league_id': self.league_id,
            'title': self.title,
            'description': self.description,
            'type': self.ticket_type,
            'options': self.options,
            'target_value': self.target_value,
            'status': self.status,
            'resolution': self.resolution,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'closes_at': self.closes_at,
            'resolved_at': self.resolved_at
        }

    @classmethod
    def get_by_id(cls, ticket_id: str) -> Optional['Ticket']:
        """Get ticket by ID"""
        try:
            db = get_db()
            ticket_data = db.get_collection('tickets').find_one(
                {'_id': ObjectId(ticket_id)})
            if ticket_data:
                return cls._from_dict(ticket_data)
            return None
        except Exception as e:
            print(f"Error getting ticket by ID: {e}")
            return None

    @classmethod
    def get_league_tickets(cls, league_id: ObjectId, status: str = None) -> List['Ticket']:
        """Get all tickets for a league"""
        try:
            db = get_db()
            query = {'league_id': league_id}
            if status:
                query['status'] = status

            tickets_data = db.get_collection(
                'tickets').find(query).sort('created_at', -1)
            return [cls._from_dict(ticket_data) for ticket_data in tickets_data]
        except Exception as e:
            print(f"Error getting league tickets: {e}")
            return []

    @classmethod
    def get_open_tickets(cls, league_id: ObjectId) -> List['Ticket']:
        """Get all open tickets for a league"""
        return cls.get_league_tickets(league_id, 'open')

    @classmethod
    def get_resolved_tickets(cls, league_id: ObjectId) -> List['Ticket']:
        """Get all resolved tickets for a league"""
        return cls.get_league_tickets(league_id, 'resolved')

    @classmethod
    def create_moneyline(cls, league_id: ObjectId, title: str, description: str,
                         options: List[Dict], created_by: ObjectId,
                         closes_at: datetime = None) -> Optional['Ticket']:
        """Create moneyline ticket"""
        try:
            ticket = cls(
                league_id=league_id,
                title=title,
                description=description,
                ticket_type='moneyline',
                options=options,
                created_by=created_by,
                closes_at=closes_at
            )
            ticket_id = ticket.save()

            if ticket_id:
                return ticket
            return None

        except Exception as e:
            print(f"Error creating moneyline ticket: {e}")
            return None

    @classmethod
    def create_over_under(cls, league_id: ObjectId, title: str, description: str,
                          target_value: float, over_odds: float, under_odds: float,
                          created_by: ObjectId, closes_at: datetime = None) -> Optional['Ticket']:
        """Create over/under ticket"""
        try:
            options = [
                {'option_text': f'Over {target_value}', 'odds': over_odds},
                {'option_text': f'Under {target_value}', 'odds': under_odds}
            ]

            ticket = cls(
                league_id=league_id,
                title=title,
                description=description,
                ticket_type='over_under',
                options=options,
                target_value=target_value,
                created_by=created_by,
                closes_at=closes_at
            )
            ticket_id = ticket.save()

            if ticket_id:
                return ticket
            return None

        except Exception as e:
            print(f"Error creating over/under ticket: {e}")
            return None

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'Ticket':
        """Create Ticket instance from database data"""
        return cls(
            _id=data.get('_id'),
            league_id=data.get('league_id'),
            title=data.get('title'),
            description=data.get('description'),
            ticket_type=data.get('type'),
            options=data.get('options', []),
            target_value=data.get('target_value'),
            status=data.get('status'),
            resolution=data.get('resolution'),
            created_by=data.get('created_by'),
            created_at=data.get('created_at'),
            closes_at=data.get('closes_at'),
            resolved_at=data.get('resolved_at')
        )

    def __repr__(self):
        return f"<Ticket {self.title}>"
