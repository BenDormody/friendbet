import os
from dotenv import load_dotenv

# Load devcontainer.env instead of .env
load_dotenv('.devcontainer/devcontainer.env')


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MongoDB Atlas URI - replace <db_password> with your actual password
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb+srv://bendormody:<db_password>@friendbet.najcag6.mongodb.net/?retryWrites=true&w=majority&appName=friendbet'
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in [
        'true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Application settings
    DEFAULT_STARTING_BALANCE = 1000
    MAX_BET_AMOUNT = 10000
    MIN_BET_AMOUNT = 1
