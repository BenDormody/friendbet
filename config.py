import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'
    MONGODB_URI = os.environ.get(
        'MONGODB_URI') or 'mongodb://localhost:27017/fantasy_betting'
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
