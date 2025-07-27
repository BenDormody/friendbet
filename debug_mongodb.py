#!/usr/bin/env python3
"""
Detailed MongoDB Atlas diagnostic script
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load devcontainer.env instead of .env
load_dotenv('.devcontainer/devcontainer.env')

def detailed_mongodb_diagnostic():
    """Run detailed diagnostics on MongoDB Atlas connection"""
    
    print("🔍 Detailed MongoDB Atlas Diagnostic")
    print("=" * 50)
    
    # Get MongoDB URI
    mongodb_uri = os.environ.get('MONGODB_URI')
    print(f"📋 MongoDB URI found: {'Yes' if mongodb_uri else 'No'}")
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in environment variables")
        return
    
    # Mask the password for security
    masked_uri = mongodb_uri.replace(mongodb_uri.split('@')[0].split(':')[-1], '***')
    print(f"🔗 Connection string: {masked_uri}")
    
    try:
        print("\n🔌 Testing connection...")
        
        # Create client
        client = MongoClient(mongodb_uri)
        
        # Test basic connection
        client.admin.command('ping')
        print("✅ Connection successful!")
        
        # List all databases
        print("\n📁 All databases in cluster:")
        databases = client.list_database_names()
        for db_name in databases:
            print(f"   - {db_name}")
        
        if not databases:
            print("   ⚠️  No databases found (this is normal for new clusters)")
        
        # Try to access friendbet database
        print(f"\n🎯 Checking 'friendbet' database...")
        db = client.friendbet
        
        # List collections in friendbet
        collections = db.list_collection_names()
        print(f"📂 Collections in 'friendbet': {collections}")
        
        if 'users' in collections:
            users_collection = db.users
            user_count = users_collection.count_documents({})
            print(f"👥 Users in 'users' collection: {user_count}")
            
            if user_count > 0:
                print("\n📋 Sample user data:")
                sample_user = users_collection.find_one()
                for key, value in sample_user.items():
                    if key == 'password_hash':
                        print(f"   {key}: {str(value)[:50]}... (truncated)")
                    else:
                        print(f"   {key}: {value}")
        else:
            print("❌ 'users' collection not found")
            
            # Try to create a test document
            print("\n🧪 Creating test document to initialize collection...")
            test_doc = {
                "test": True,
                "created_at": datetime.utcnow(),
                "message": "This is a test document to initialize the collection"
            }
            
            result = db.users.insert_one(test_doc)
            print(f"✅ Test document created with ID: {result.inserted_id}")
            
            # Check again
            collections = db.list_collection_names()
            print(f"📂 Collections after test: {collections}")
            
            # Clean up test document
            db.users.delete_one({"_id": result.inserted_id})
            print("🧹 Test document cleaned up")
        
        # Check database stats
        print(f"\n📊 Database statistics:")
        try:
            stats = db.command("dbStats")
            print(f"   Collections: {stats.get('collections', 0)}")
            print(f"   Objects: {stats.get('objects', 0)}")
            print(f"   Data size: {stats.get('dataSize', 0)} bytes")
        except Exception as e:
            print(f"   Could not get stats: {e}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")

def test_user_creation():
    """Test creating a user through the User model"""
    
    print(f"\n🧪 Testing User Model Creation")
    print("=" * 40)
    
    try:
        from models.user import User
        
        # Create a test user
        test_user = User(
            username="debug_test_user",
            email="debug@test.com"
        )
        test_user.set_password("testpass123")
        
        print("✅ User object created")
        print(f"   Username: {test_user.username}")
        print(f"   Email: {test_user.email}")
        print(f"   Password hash: {test_user.password_hash[:50]}...")
        
        # Save to database
        saved_user = test_user.save()
        print(f"✅ User saved to database with ID: {saved_user._id}")
        
        # Verify it exists
        from database import get_db
        db = get_db()
        found_user = db.users.find_one({"_id": saved_user._id})
        
        if found_user:
            print("✅ User found in database!")
            print(f"   Database ID: {found_user['_id']}")
            print(f"   Username: {found_user['username']}")
        else:
            print("❌ User not found in database")
        
        # Clean up
        db.users.delete_one({"_id": saved_user._id})
        print("🧹 Test user cleaned up")
        
    except Exception as e:
        print(f"❌ Error testing user creation: {e}")

if __name__ == "__main__":
    detailed_mongodb_diagnostic()
    test_user_creation()
    
    print(f"\n" + "=" * 60)
    print("💡 Troubleshooting Tips:")
    print("1. Make sure you're looking at the correct cluster in Atlas")
    print("2. Try refreshing the Atlas dashboard")
    print("3. Check if you have the correct permissions")
    print("4. The database/collection might not show until you insert data")
    print("5. Try clicking 'Browse Collections' in Atlas")
    print("6. Look for database 'friendbet' and collection 'users'") 