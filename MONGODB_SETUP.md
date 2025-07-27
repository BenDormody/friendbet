# MongoDB Atlas Setup Guide

## 🔧 **Step 1: Create .env File**

Create a `.env` file in your project root with your MongoDB Atlas credentials:

```bash
# Create .env file
touch .env
```

Add the following content to `.env`:

```env
# MongoDB Atlas Configuration
# Replace YOUR_ACTUAL_PASSWORD with your real MongoDB Atlas password
MONGODB_URI=mongodb+srv://bendormody:YOUR_ACTUAL_PASSWORD@friendbet.najcag6.mongodb.net/?retryWrites=true&w=majority&appName=friendbet

# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
```

## 🔍 **Step 2: Test MongoDB Connection**

Run the test script to verify your connection:

```bash
python test_mongodb.py
```

This will:
- ✅ Test the connection to MongoDB Atlas
- ✅ Verify database access
- ✅ Check existing collections
- ✅ Test user creation/deletion

## 🚀 **Step 3: Start the Application**

Once the connection test passes:

```bash
python app.py
```

The app should now start on `http://localhost:5001`

## 🔐 **Step 4: Test Authentication**

1. Open `http://localhost:5001` in your browser
2. Click "Sign Up" to create a new user
3. Check your MongoDB Atlas dashboard to see the user created in the `users` collection

## 🛠️ **Troubleshooting**

### ❌ **Connection Failed**
- Verify your password in the `.env` file
- Check that your IP is whitelisted in MongoDB Atlas
- Ensure your Atlas cluster is running

### ❌ **Database Not Found**
- The database `friendbet` will be created automatically when you first insert data
- Collections (`users`, `leagues`, etc.) will be created automatically

### ❌ **Authentication Errors**
- Make sure you're using the correct username (`bendormody`)
- Verify the password is correct
- Check that your Atlas user has read/write permissions

## 📊 **MongoDB Atlas Dashboard**

You can monitor your database at:
- **Cluster**: `friendbet.najcag6.mongodb.net`
- **Database**: `friendbet`
- **Collections**: `users`, `leagues`, `tickets`, `bets`

## 🔒 **Security Notes**

- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore`
- Use strong passwords for your Atlas user
- Consider using Atlas App Users for production

## 📝 **Expected Database Schema**

After successful registration, you should see:

### Users Collection
```json
{
  "_id": ObjectId,
  "username": "testuser",
  "email": "test@example.com",
  "password_hash": "hashed_password_string",
  "created_at": "2024-01-15T10:30:00Z",
  "leagues": []
}
```

## 🎯 **Next Steps**

Once authentication is working:
1. Test user registration and login
2. Create your first league
3. Invite friends to join
4. Start placing bets! 