from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime
from database import get_db
from typing import Optional, List, Dict, Any

class User(UserMixin):
    """User model for authentication and profile management"""
    
    def __init__(self, username: str = None, email: str = None, password_hash: str = None, 
                 created_at: datetime = None, leagues: List[ObjectId] = None, _id: ObjectId = None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.leagues = leagues or []
        self._id = _id
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self._id) if self._id else None
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def save(self) -> ObjectId:
        """Save user to database"""
        db = get_db()
        user_data = {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'leagues': self.leagues
        }
        
        if self._id:
            # Update existing user
            result = db.get_collection('users').update_one(
                {'_id': self._id},
                {'$set': user_data}
            )
            return self._id if result.modified_count > 0 else None
        else:
            # Create new user
            result = db.get_collection('users').insert_one(user_data)
            self._id = result.inserted_id
            return self._id
    
    def add_league(self, league_id: ObjectId):
        """Add league to user's league list"""
        if league_id not in self.leagues:
            self.leagues.append(league_id)
            self.save()
    
    def remove_league(self, league_id: ObjectId):
        """Remove league from user's league list"""
        if league_id in self.leagues:
            self.leagues.remove(league_id)
            self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at,
            'leagues': self.leagues
        }
    
    @classmethod
    def get_by_id(cls, user_id: str) -> Optional['User']:
        """Get user by ID"""
        try:
            db = get_db()
            user_data = db.get_collection('users').find_one({'_id': ObjectId(user_id)})
            if user_data:
                return cls._from_dict(user_data)
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Get user by email"""
        try:
            db = get_db()
            user_data = db.get_collection('users').find_one({'email': email})
            if user_data:
                return cls._from_dict(user_data)
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """Get user by username"""
        try:
            db = get_db()
            user_data = db.get_collection('users').find_one({'username': username})
            if user_data:
                return cls._from_dict(user_data)
            return None
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    @classmethod
    def create(cls, username: str, email: str, password: str) -> Optional['User']:
        """Create new user"""
        try:
            # Check if user already exists
            if cls.get_by_email(email):
                raise ValueError("Email already registered")
            if cls.get_by_username(username):
                raise ValueError("Username already taken")
            
            user = cls(username=username, email=email)
            user.set_password(password)
            user_id = user.save()
            
            if user_id:
                return user
            return None
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User instance from database data"""
        return cls(
            _id=data.get('_id'),
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            created_at=data.get('created_at'),
            leagues=data.get('leagues', [])
        )
    
    def __repr__(self):
        return f"<User {self.username}>"
