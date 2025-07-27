from flask_login import LoginManager
from models.user import User

# Initialize login manager
login_manager = LoginManager() 

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.get_by_id(user_id) 