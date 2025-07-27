from datetime import datetime
from bson import ObjectId
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db


class User(UserMixin):
    def __init__(self, username, email, password_hash=None, _id=None, created_at=None, leagues=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self._id = _id
        self.created_at = created_at or datetime.utcnow()
        self.leagues = leagues or []

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self._id)

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User._from_dict(user_data)
        return None

    @staticmethod
    def get_by_username(username):
        db = get_db()
        user_data = db.users.find_one({'username': username})
        if user_data:
            return User._from_dict(user_data)
        return None

    @staticmethod
    def get_by_email(email):
        db = get_db()
        user_data = db.users.find_one({'email': email})
        if user_data:
            return User._from_dict(user_data)
        return None

    def save(self):
        db = get_db()
        if self._id is None:
            # New user
            user_data = {
                'username': self.username,
                'email': self.email,
                'password_hash': self.password_hash,
                'created_at': self.created_at,
                'leagues': self.leagues
            }
            result = db.users.insert_one(user_data)
            self._id = result.inserted_id
        else:
            # Update existing user
            db.users.update_one(
                {'_id': self._id},
                {
                    '$set': {
                        'username': self.username,
                        'email': self.email,
                        'password_hash': self.password_hash,
                        'leagues': self.leagues
                    }
                }
            )
        return self

    def add_league(self, league_id):
        if str(league_id) not in self.leagues:
            self.leagues.append(str(league_id))
            self.save()

    def remove_league(self, league_id):
        if str(league_id) in self.leagues:
            self.leagues.remove(str(league_id))
            self.save()

    @staticmethod
    def _from_dict(user_data):
        return User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            _id=user_data['_id'],
            created_at=user_data['created_at'],
            leagues=user_data.get('leagues', [])
        )
