#!/usr/bin/env python3
"""
Script to check and count users in MongoDB Atlas database
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load devcontainer.env instead of .env
load_dotenv('.devcontainer/devcontainer.env')

def check_users_in_database():
    """Check and display users in the database"""
    
    # Get MongoDB URI from environment
    mongodb_uri = os.environ.get('MONGODB_URI')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in environment variables")
        return
    
    try:
        print("🔍 Checking users in MongoDB Atlas...")
        print("=" * 50)
        
        # Create client
        client = MongoClient(mongodb_uri)
        
        # Access the database
        db = client.friendbet
        
        # Get users collection
        users_collection = db.users
        
        # Count total users
        total_users = users_collection.count_documents({})
        print(f"👥 Total users in database: {total_users}")
        
        if total_users == 0:
            print("📝 No users found. Try registering a user first!")
            return
        
        # Get all users (without password hashes for security)
        users = list(users_collection.find({}, {
            'username': 1, 
            'email': 1, 
            'created_at': 1, 
            'leagues': 1,
            '_id': 1
        }))
        
        print(f"\n📋 User Details (showing {len(users)} users):")
        print("-" * 50)
        
        for i, user in enumerate(users, 1):
            print(f"\n👤 User #{i}:")
            print(f"   ID: {user['_id']}")
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Created: {user['created_at']}")
            print(f"   Leagues: {len(user.get('leagues', []))} leagues")
            
            # Show leagues if any
            if user.get('leagues'):
                print(f"   League IDs: {user['leagues']}")
        
        # Show database and collection info
        print(f"\n📊 Database Information:")
        print("-" * 30)
        print(f"Database: {db.name}")
        print(f"Collection: users")
        print(f"Total documents: {total_users}")
        
        # List all collections in database
        collections = db.list_collection_names()
        print(f"All collections: {collections}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error checking users: {e}")

def create_test_user():
    """Create a test user to verify the system is working"""
    
    mongodb_uri = os.environ.get('MONGODB_URI')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found")
        return
    
    try:
        print("\n🧪 Creating test user...")
        
        client = MongoClient(mongodb_uri)
        db = client.friendbet
        users_collection = db.users
        
        # Check if test user already exists
        existing_user = users_collection.find_one({"username": "test_user_check"})
        
        if existing_user:
            print("ℹ️  Test user already exists")
            return
        
        # Create test user
        test_user = {
            "username": "test_user_check",
            "email": "test_check@example.com",
            "password_hash": "test_hash_for_checking",
            "created_at": datetime.utcnow(),
            "leagues": []
        }
        
        result = users_collection.insert_one(test_user)
        print(f"✅ Test user created with ID: {result.inserted_id}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")

if __name__ == "__main__":
    print("🔍 MongoDB Atlas User Checker")
    print("=" * 40)
    
    # Check existing users
    check_users_in_database()
    
    # Ask if user wants to create a test user
    print(f"\n" + "=" * 50)
    print("💡 Tips for checking your MongoDB Atlas dashboard:")
    print("1. Go to MongoDB Atlas dashboard")
    print("2. Click on your cluster: friendbet.najcag6.mongodb.net")
    print("3. Click 'Browse Collections'")
    print("4. Look for database 'friendbet'")
    print("5. Look for collection 'users'")
    print("6. You should see your users listed there")
    print("\n🔒 Note: Passwords are hashed for security - you'll see long encrypted strings instead of plain text passwords") 