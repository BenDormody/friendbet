from bson import ObjectId
from datetime import datetime, timedelta
from database import get_db
from typing import Optional, List, Dict, Any
import secrets
import string

class League:
    """League model for managing betting leagues"""
    
    def __init__(self, name: str = None, description: str = None, creator_id: ObjectId = None,
                 starting_balance: float = 1000.0, status: str = 'active',
                 created_at: datetime = None, end_date: datetime = None,
                 invite_code: str = None, _id: ObjectId = None):
        self.name = name
        self.description = description
        self.creator_id = creator_id
        self.admins = [creator_id] if creator_id else []
        self.members = []
        self.starting_balance = starting_balance
        self.status = status  # 'active', 'completed', 'paused'
        self.created_at = created_at or datetime.utcnow()
        self.end_date = end_date
        self.invite_code = invite_code or self._generate_invite_code()
        self._id = _id
    
    def _generate_invite_code(self) -> str:
        """Generate unique invite code"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(8))
    
    def add_member(self, user_id: ObjectId, user_username: str) -> bool:
        """Add member to league"""
        # Check if user is already a member
        for member in self.members:
            if member['user_id'] == user_id:
                return False
        
        # Add new member
        member_data = {
            'user_id': user_id,
            'username': user_username,
            'balance': self.starting_balance,
            'joined_at': datetime.utcnow()
        }
        self.members.append(member_data)
        return True
    
    def remove_member(self, user_id: ObjectId) -> bool:
        """Remove member from league"""
        for i, member in enumerate(self.members):
            if member['user_id'] == user_id:
                del self.members[i]
                return True
        return False
    
    def get_member(self, user_id: ObjectId) -> Optional[Dict[str, Any]]:
        """Get member data by user ID"""
        for member in self.members:
            if member['user_id'] == user_id:
                return member
        return None
    
    def update_member_balance(self, user_id: ObjectId, new_balance: float) -> bool:
        """Update member's balance"""
        for member in self.members:
            if member['user_id'] == user_id:
                member['balance'] = new_balance
                return True
        return False
    
    def is_admin(self, user_id: ObjectId) -> bool:
        """Check if user is admin"""
        return user_id in self.admins
    
    def promote_to_admin(self, user_id: ObjectId) -> bool:
        """Promote user to admin"""
        if user_id not in self.admins:
            self.admins.append(user_id)
            return True
        return False
    
    def demote_from_admin(self, user_id: ObjectId) -> bool:
        """Demote admin to regular member"""
        if user_id in self.admins and user_id != self.creator_id:
            self.admins.remove(user_id)
            return True
        return False
    
    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Get sorted leaderboard by balance"""
        return sorted(self.members, key=lambda x: x['balance'], reverse=True)
    
    def save(self) -> ObjectId:
        """Save league to database"""
        db = get_db()
        league_data = {
            'name': self.name,
            'description': self.description,
            'creator_id': self.creator_id,
            'admins': self.admins,
            'members': self.members,
            'starting_balance': self.starting_balance,
            'status': self.status,
            'created_at': self.created_at,
            'end_date': self.end_date,
            'invite_code': self.invite_code
        }
        
        if self._id:
            # Update existing league
            result = db.get_collection('leagues').update_one(
                {'_id': self._id},
                {'$set': league_data}
            )
            return self._id if result.modified_count > 0 else None
        else:
            # Create new league
            result = db.get_collection('leagues').insert_one(league_data)
            self._id = result.inserted_id
            return self._id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert league to dictionary"""
        return {
            '_id': self._id,
            'name': self.name,
            'description': self.description,
            'creator_id': self.creator_id,
            'admins': self.admins,
            'members': self.members,
            'starting_balance': self.starting_balance,
            'status': self.status,
            'created_at': self.created_at,
            'end_date': self.end_date,
            'invite_code': self.invite_code
        }
    
    @classmethod
    def get_by_id(cls, league_id: str) -> Optional['League']:
        """Get league by ID"""
        try:
            db = get_db()
            league_data = db.get_collection('leagues').find_one({'_id': ObjectId(league_id)})
            if league_data:
                return cls._from_dict(league_data)
            return None
        except Exception as e:
            print(f"Error getting league by ID: {e}")
            return None
    
    @classmethod
    def get_by_invite_code(cls, invite_code: str) -> Optional['League']:
        """Get league by invite code"""
        try:
            db = get_db()
            league_data = db.get_collection('leagues').find_one({'invite_code': invite_code})
            if league_data:
                return cls._from_dict(league_data)
            return None
        except Exception as e:
            print(f"Error getting league by invite code: {e}")
            return None
    
    @classmethod
    def get_user_leagues(cls, user_id: ObjectId) -> List['League']:
        """Get all leagues for a user"""
        try:
            db = get_db()
            leagues_data = db.get_collection('leagues').find({
                'members.user_id': user_id
            })
            return [cls._from_dict(league_data) for league_data in leagues_data]
        except Exception as e:
            print(f"Error getting user leagues: {e}")
            return []
    
    @classmethod
    def create(cls, name: str, description: str, creator_id: ObjectId, 
               starting_balance: float = 1000.0) -> Optional['League']:
        """Create new league"""
        try:
            league = cls(
                name=name,
                description=description,
                creator_id=creator_id,
                starting_balance=starting_balance
            )
            league_id = league.save()
            
            if league_id:
                return league
            return None
            
        except Exception as e:
            print(f"Error creating league: {e}")
            return None
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'League':
        """Create League instance from database data"""
        league = cls(
            _id=data.get('_id'),
            name=data.get('name'),
            description=data.get('description'),
            creator_id=data.get('creator_id'),
            starting_balance=data.get('starting_balance'),
            status=data.get('status'),
            created_at=data.get('created_at'),
            end_date=data.get('end_date'),
            invite_code=data.get('invite_code')
        )
        # Restore members and admins from database
        league.members = data.get('members', [])
        league.admins = data.get('admins', [league.creator_id] if league.creator_id else [])
        return league
    
    def __repr__(self):
        return f"<League {self.name}>"
