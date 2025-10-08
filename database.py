from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config
import logging
import certifi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Database connection manager"""

    def __init__(self, app=None):
        self.client = None
        self.db = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize database connection"""
        try:
            # Parse MongoDB URI to extract connection parameters
            mongodb_uri = app.config['MONGODB_URI']

            # Connection options for better reliability
            connection_options = {
                'serverSelectionTimeoutMS': app.config.get('MONGODB_SERVER_SELECTION_TIMEOUT_MS', 5000),
                'connectTimeoutMS': app.config.get('MONGODB_CONNECT_TIMEOUT_MS', 10000),
                'socketTimeoutMS': app.config.get('MONGODB_SOCKET_TIMEOUT_MS', 20000),
                'retryWrites': True,
                'retryReads': True,
                'maxPoolSize': 50,
                'minPoolSize': 5,
                'maxIdleTimeMS': 30000,
                'waitQueueTimeoutMS': 5000,
                'tlsCAFile': certifi.where()  # Use certifi for TLS certificates
            }

            self.client = MongoClient(mongodb_uri, **connection_options)

            # Test the connection
            self.client.server_info()

            # Get database name from URI
            db_name = self._extract_database_name(mongodb_uri)
            self.db = self.client[db_name]

            # Create indexes for better performance
            self.create_indexes()

            logger.info(f"✅ Connected to MongoDB database: {db_name}")
            logger.info(
                f"📍 Connection URI: {mongodb_uri.replace(mongodb_uri.split('@')[0].split('://')[1], '***') if '@' in mongodb_uri else mongodb_uri}")

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            logger.error(f"📍 URI: {mongodb_uri}")
            raise

    def _extract_database_name(self, uri):
        """Extract database name from MongoDB URI"""
        try:
            # Handle different URI formats
            if '?' in uri:
                # Remove query parameters
                uri = uri.split('?')[0]

            # Split by '/' and get the last part
            parts = uri.split('/')
            if len(parts) > 3:
                db_name = parts[-1]
                # Remove any trailing characters
                db_name = db_name.split('?')[0].split('#')[0]
                return db_name if db_name else 'fantasy_betting'
            else:
                return 'fantasy_betting'
        except Exception as e:
            logger.warning(
                f"Could not extract database name from URI, using default: {e}")
            return 'fantasy_betting'

    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            self.db.users.create_index("email", unique=True)
            self.db.users.create_index("username", unique=True)

            # Leagues collection indexes
            self.db.leagues.create_index(
                "invite_code", unique=True, sparse=True)
            self.db.leagues.create_index("creator_id")
            self.db.leagues.create_index("members.user_id")

            # Tickets collection indexes
            self.db.tickets.create_index("league_id")
            self.db.tickets.create_index("status")
            self.db.tickets.create_index("created_by")
            self.db.tickets.create_index([("league_id", 1), ("status", 1)])

            # Bets collection indexes
            self.db.bets.create_index("user_id")
            self.db.bets.create_index("league_id")
            self.db.bets.create_index("ticket_id")
            self.db.bets.create_index("status")
            self.db.bets.create_index([("user_id", 1), ("league_id", 1)])

            logger.info("Database indexes created successfully")

        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    def get_collection(self, collection_name):
        """Get a collection from the database"""
        return self.db[collection_name]

    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database instance
db = Database()


def get_db():
    """Get database instance"""
    return db
