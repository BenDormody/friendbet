import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'
    MONGODB_URI = os.environ.get(
        'MONGODB_URI') or 'mongodb://localhost:27017/fantasy_betting'
    MONGO_URI = MONGODB_URI  # Alias for compatibility

    # MongoDB connection settings
    MONGODB_CONNECT_TIMEOUT_MS = 10000  # 10 seconds
    MONGODB_SERVER_SELECTION_TIMEOUT_MS = 5000  # 5 seconds
    MONGODB_SOCKET_TIMEOUT_MS = 20000  # 20 seconds

    # Flask-Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in [
        'true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Application settings
    PER_PAGE = 20  # Items per page for pagination
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Betting settings
    DEFAULT_STARTING_BALANCE = 1000.0
    MIN_BET_AMOUNT = 1.0
    MAX_BET_AMOUNT = 10000.0


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/fantasy_betting_test'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
