from bson import ObjectId
from datetime import datetime
from database import get_db
from typing import Optional, List, Dict, Any

class Bet:
    """Bet model for managing user bets"""
    
    def __init__(self, user_id: ObjectId = None, league_id: ObjectId = None,
                 ticket_id: ObjectId = None, amount: float = None,
                 selected_option: str = None, potential_payout: float = None,
                 status: str = 'pending', placed_at: datetime = None, _id: ObjectId = None):
        self.user_id = user_id
        self.league_id = league_id
        self.ticket_id = ticket_id
        self.amount = amount
        self.selected_option = selected_option
        self.potential_payout = potential_payout
        self.status = status  # 'pending', 'won', 'lost'
        self.placed_at = placed_at or datetime.utcnow()
        self._id = _id
    
    def calculate_payout(self, odds: float) -> float:
        """Calculate potential payout based on odds"""
        return float(self.amount) * float(odds)
    
    def mark_won(self) -> bool:
        """Mark bet as won"""
        if self.status == 'pending':
            self.status = 'won'
            return True
        return False
    
    def mark_lost(self) -> bool:
        """Mark bet as lost"""
        if self.status == 'pending':
            self.status = 'lost'
            return True
        return False
    
    def is_winner(self) -> bool:
        """Check if bet is a winner"""
        return self.status == 'won'
    
    def is_loser(self) -> bool:
        """Check if bet is a loser"""
        return self.status == 'lost'
    
    def is_pending(self) -> bool:
        """Check if bet is still pending"""
        return self.status == 'pending'
    
    def save(self) -> ObjectId:
        """Save bet to database"""
        db = get_db()
        bet_data = {
            'user_id': self.user_id,
            'league_id': self.league_id,
            'ticket_id': self.ticket_id,
            'amount': self.amount,
            'selected_option': self.selected_option,
            'potential_payout': self.potential_payout,
            'status': self.status,
            'placed_at': self.placed_at
        }
        
        if self._id:
            # Update existing bet
            result = db.get_collection('bets').update_one(
                {'_id': self._id},
                {'$set': bet_data}
            )
            return self._id if result.modified_count > 0 else None
        else:
            # Create new bet
            result = db.get_collection('bets').insert_one(bet_data)
            self._id = result.inserted_id
            return self._id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert bet to dictionary"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'league_id': self.league_id,
            'ticket_id': self.ticket_id,
            'amount': self.amount,
            'selected_option': self.selected_option,
            'potential_payout': self.potential_payout,
            'status': self.status,
            'placed_at': self.placed_at
        }
    
    @classmethod
    def get_by_id(cls, bet_id: str) -> Optional['Bet']:
        """Get bet by ID"""
        try:
            db = get_db()
            bet_data = db.get_collection('bets').find_one({'_id': ObjectId(bet_id)})
            if bet_data:
                return cls._from_dict(bet_data)
            return None
        except Exception as e:
            print(f"Error getting bet by ID: {e}")
            return None
    
    @classmethod
    def get_user_bets(cls, user_id: ObjectId, league_id: ObjectId = None) -> List['Bet']:
        """Get all bets for a user"""
        try:
            db = get_db()
            query = {'user_id': user_id}
            if league_id:
                query['league_id'] = league_id
            
            bets_data = db.get_collection('bets').find(query).sort('placed_at', -1)
            return [cls._from_dict(bet_data) for bet_data in bets_data]
        except Exception as e:
            print(f"Error getting user bets: {e}")
            return []
    
    @classmethod
    def get_ticket_bets(cls, ticket_id: ObjectId) -> List['Bet']:
        """Get all bets for a specific ticket"""
        try:
            db = get_db()
            bets_data = db.get_collection('bets').find({'ticket_id': ticket_id}).sort('placed_at', -1)
            return [cls._from_dict(bet_data) for bet_data in bets_data]
        except Exception as e:
            print(f"Error getting ticket bets: {e}")
            return []
    
    @classmethod
    def get_league_bets(cls, league_id: ObjectId, status: str = None) -> List['Bet']:
        """Get all bets for a league"""
        try:
            db = get_db()
            query = {'league_id': league_id}
            if status:
                query['status'] = status
            
            bets_data = db.get_collection('bets').find(query).sort('placed_at', -1)
            return [cls._from_dict(bet_data) for bet_data in bets_data]
        except Exception as e:
            print(f"Error getting league bets: {e}")
            return []
    
    @classmethod
    def get_user_ticket_bet(cls, user_id: ObjectId, ticket_id: ObjectId) -> Optional['Bet']:
        """Get user's bet for a specific ticket"""
        try:
            db = get_db()
            bet_data = db.get_collection('bets').find_one({
                'user_id': user_id,
                'ticket_id': ticket_id
            })
            if bet_data:
                return cls._from_dict(bet_data)
            return None
        except Exception as e:
            print(f"Error getting user ticket bet: {e}")
            return None
    
    @classmethod
    def create_bet(cls, user_id: ObjectId, league_id: ObjectId, ticket_id: ObjectId,
                  amount: float, selected_option: str, odds: float) -> Optional['Bet']:
        """Create new bet"""
        try:
            potential_payout = amount * odds
            
            bet = cls(
                user_id=user_id,
                league_id=league_id,
                ticket_id=ticket_id,
                amount=amount,
                selected_option=selected_option,
                potential_payout=potential_payout
            )
            bet_id = bet.save()
            
            if bet_id:
                return bet
            return None
            
        except Exception as e:
            print(f"Error creating bet: {e}")
            return None
    
    @classmethod
    def resolve_bets(cls, ticket_id: ObjectId, winning_option: str) -> Dict[str, int]:
        """Resolve all bets for a ticket"""
        try:
            db = get_db()
            bets = cls.get_ticket_bets(ticket_id)
            
            won_count = 0
            lost_count = 0
            
            for bet in bets:
                if bet.selected_option == winning_option:
                    bet.mark_won()
                    won_count += 1
                else:
                    bet.mark_lost()
                    lost_count += 1
                
                bet.save()
            
            return {
                'won': won_count,
                'lost': lost_count,
                'total': len(bets)
            }
            
        except Exception as e:
            print(f"Error resolving bets: {e}")
            return {'won': 0, 'lost': 0, 'total': 0}
    
    @classmethod
    def get_user_stats(cls, user_id: ObjectId, league_id: ObjectId = None) -> Dict[str, Any]:
        """Get user betting statistics"""
        try:
            bets = cls.get_user_bets(user_id, league_id)
            
            total_bets = len(bets)
            won_bets = len([bet for bet in bets if bet.is_winner()])
            lost_bets = len([bet for bet in bets if bet.is_loser()])
            pending_bets = len([bet for bet in bets if bet.is_pending()])
            
            total_wagered = sum(bet.amount for bet in bets)
            total_winnings = sum(bet.potential_payout for bet in bets if bet.is_winner())
            
            win_rate = (won_bets / total_bets * 100) if total_bets > 0 else 0
            
            return {
                'total_bets': total_bets,
                'won_bets': won_bets,
                'lost_bets': lost_bets,
                'pending_bets': pending_bets,
                'total_wagered': total_wagered,
                'total_winnings': total_winnings,
                'win_rate': round(win_rate, 2),
                'net_profit': total_winnings - total_wagered
            }
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {
                'total_bets': 0,
                'won_bets': 0,
                'lost_bets': 0,
                'pending_bets': 0,
                'total_wagered': 0,
                'total_winnings': 0,
                'win_rate': 0,
                'net_profit': 0
            }
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'Bet':
        """Create Bet instance from database data"""
        return cls(
            _id=data.get('_id'),
            user_id=data.get('user_id'),
            league_id=data.get('league_id'),
            ticket_id=data.get('ticket_id'),
            amount=data.get('amount'),
            selected_option=data.get('selected_option'),
            potential_payout=data.get('potential_payout'),
            status=data.get('status'),
            placed_at=data.get('placed_at')
        )
    
    def __repr__(self):
        return f"<Bet {self.amount} on {self.selected_option}>"
