from datetime import datetime
from bson import ObjectId
import secrets
from database import get_db


class League:
    def __init__(self, name, description, creator_id, starting_balance=1000, _id=None,
                 admins=None, members=None, status='active', created_at=None,
                 end_date=None, invite_code=None):
        self.name = name
        self.description = description
        self.creator_id = creator_id
        self.starting_balance = starting_balance
        self._id = _id
        self.admins = admins or [str(creator_id)]
        self.members = members or []
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.end_date = end_date
        self.invite_code = invite_code or self._generate_invite_code()

    def _generate_invite_code(self):
        return secrets.token_urlsafe(8)

    @staticmethod
    def get_by_id(league_id):
        db = get_db()
        league_data = db.leagues.find_one({'_id': ObjectId(league_id)})
        if league_data:
            return League._from_dict(league_data)
        return None

    @staticmethod
    def get_by_invite_code(invite_code):
        db = get_db()
        league_data = db.leagues.find_one({'invite_code': invite_code})
        if league_data:
            return League._from_dict(league_data)
        return None

    @staticmethod
    def get_user_leagues(user_id):
        db = get_db()
        leagues_data = db.leagues.find({
            '$or': [
                {'members.user_id': str(user_id)},
                {'admins': str(user_id)}
            ]
        })
        return [League._from_dict(league_data) for league_data in leagues_data]

    def save(self):
        db = get_db()
        if self._id is None:
            # New league
            league_data = {
                'name': self.name,
                'description': self.description,
                'creator_id': str(self.creator_id),
                'starting_balance': self.starting_balance,
                'admins': self.admins,
                'members': self.members,
                'status': self.status,
                'created_at': self.created_at,
                'end_date': self.end_date,
                'invite_code': self.invite_code
            }
            result = db.leagues.insert_one(league_data)
            self._id = result.inserted_id
        else:
            # Update existing league
            db.leagues.update_one(
                {'_id': self._id},
                {
                    '$set': {
                        'name': self.name,
                        'description': self.description,
                        'starting_balance': self.starting_balance,
                        'admins': self.admins,
                        'members': self.members,
                        'status': self.status,
                        'end_date': self.end_date,
                        'invite_code': self.invite_code
                    }
                }
            )
        return self

    def add_member(self, user_id, balance=None):
        if balance is None:
            balance = self.starting_balance

        # Check if user is already a member
        for member in self.members:
            if member['user_id'] == str(user_id):
                return False

        new_member = {
            'user_id': str(user_id),
            'balance': balance,
            'joined_at': datetime.utcnow()
        }
        self.members.append(new_member)
        self.save()
        return True

    def remove_member(self, user_id):
        self.members = [
            m for m in self.members if m['user_id'] != str(user_id)]
        if str(user_id) in self.admins:
            self.admins.remove(str(user_id))
        self.save()

    def add_admin(self, user_id):
        if str(user_id) not in self.admins:
            self.admins.append(str(user_id))
            self.save()

    def remove_admin(self, user_id):
        if str(user_id) in self.admins and str(user_id) != str(self.creator_id):
            self.admins.remove(str(user_id))
            self.save()

    def get_member_balance(self, user_id):
        for member in self.members:
            if member['user_id'] == str(user_id):
                return member['balance']
        return None

    def update_member_balance(self, user_id, new_balance):
        for member in self.members:
            if member['user_id'] == str(user_id):
                member['balance'] = new_balance
                self.save()
                return True
        return False

    def is_admin(self, user_id):
        return str(user_id) in self.admins

    def is_creator(self, user_id):
        return str(user_id) == str(self.creator_id)

    def is_member(self, user_id):
        return any(m['user_id'] == str(user_id) for m in self.members)

    def get_leaderboard(self):
        return sorted(self.members, key=lambda x: x['balance'], reverse=True)

    @staticmethod
    def _from_dict(league_data):
        return League(
            name=league_data['name'],
            description=league_data['description'],
            creator_id=league_data['creator_id'],
            starting_balance=league_data.get('starting_balance', 1000),
            _id=league_data['_id'],
            admins=league_data.get('admins', []),
            members=league_data.get('members', []),
            status=league_data.get('status', 'active'),
            created_at=league_data['created_at'],
            end_date=league_data.get('end_date'),
            invite_code=league_data.get('invite_code')
        )
