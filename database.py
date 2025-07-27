from pymongo import MongoClient
from flask import current_app
import logging

logger = logging.getLogger(__name__)


def get_db():
    try:
        uri = current_app.config['MONGODB_URI']
        logger.info(f"Connecting to MongoDB Atlas...")
        
        # Create client
        client = MongoClient(uri)
        
        # Test the connection
        client.admin.command('ping')
        logger.info("MongoDB Atlas connection successful!")
        
        # Use the specific database name 'friendbet' for your Atlas cluster
        db = client.friendbet
        
        # Test database access
        db.list_collection_names()
        logger.info("Database 'friendbet' accessed successfully!")
        
        return db
        
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        raise Exception(f"Failed to connect to MongoDB Atlas: {e}") 