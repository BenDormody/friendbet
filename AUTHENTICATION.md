# Authentication System Documentation

## Overview

The Fantasy Betting League application now has a fully functional authentication system using Flask-Login and MongoDB. Users can register, login, and logout with proper session management.

## Features Implemented

### ✅ User Registration
- Username, email, and password validation
- Password hashing using Werkzeug
- Duplicate username/email checking
- MongoDB storage

### ✅ User Login
- Email or username login support
- Password verification
- Session management with Flask-Login
- Automatic UI updates after login

### ✅ User Logout
- Secure session termination
- UI updates after logout

### ✅ Authentication State Management
- Real-time authentication status checking
- Dynamic UI updates based on auth state
- Protected route access

## API Endpoints

### Registration
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com", 
  "password": "testpass123"
}
```

**Response:**
```json
{
  "message": "Registration successful! Please log in.",
  "user": {
    "id": "68868cfca39b910a9eae3f22",
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "testpass123"
}
```

**Response:**
```json
{
  "message": "Login successful!",
  "user": {
    "id": "68868cfca39b910a9eae3f22",
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### Logout
```
POST /api/auth/logout
```

**Response:**
```json
{
  "message": "Logout successful!"
}
```

### Check Authentication Status
```
GET /api/auth/check
```

**Authenticated Response:**
```json
{
  "authenticated": true,
  "user": {
    "id": "68868cfca39b910a9eae3f22",
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

**Unauthenticated Response:**
```json
{
  "authenticated": false
}
```

## Frontend Integration

### JavaScript Functions
The authentication is fully integrated with the frontend through the `FantasyBetting` namespace:

- `FantasyBetting.showLoginModal()` - Opens login modal
- `FantasyBetting.showRegisterModal()` - Opens registration modal
- `FantasyBetting.logout()` - Logs out the current user
- `FantasyBetting.currentUser()` - Returns current user object

### UI Updates
- Navigation automatically updates to show login/logout buttons
- Welcome message displays when authenticated
- Modals show appropriate error messages
- Loading states during authentication requests

### Protected Features
- Creating leagues requires authentication
- Joining leagues requires authentication
- Viewing league details requires authentication

## Database Schema

### Users Collection
```json
{
  "_id": ObjectId,
  "username": "string",
  "email": "string", 
  "password_hash": "string",
  "created_at": "datetime",
  "leagues": ["league_id_array"]
}
```

## Security Features

- **Password Hashing**: Uses Werkzeug's `generate_password_hash()` and `check_password_hash()`
- **Session Management**: Flask-Login handles secure session creation and validation
- **Input Validation**: Server-side validation of all registration/login data
- **Error Handling**: Proper error messages without exposing sensitive information
- **CSRF Protection**: Flask-WTF provides CSRF protection for forms

## Testing

The authentication system has been tested with:

1. ✅ User registration with valid data
2. ✅ User registration with duplicate username/email (error handling)
3. ✅ User login with correct credentials
4. ✅ User login with incorrect credentials (error handling)
5. ✅ Authentication status checking
6. ✅ User logout
7. ✅ Session persistence across requests

## Usage Examples

### Starting the Application
```bash
python app.py
```

### Testing with curl
```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  -c cookies.txt

# Check auth status
curl -X GET http://localhost:5000/api/auth/check -b cookies.txt

# Logout
curl -X POST http://localhost:5000/api/auth/logout -b cookies.txt
```

## Next Steps

1. **Email Verification**: Add email verification for new registrations
2. **Password Reset**: Implement password reset functionality
3. **Profile Management**: Add user profile editing capabilities
4. **Social Login**: Integrate OAuth providers (Google, Facebook, etc.)
5. **Two-Factor Authentication**: Add 2FA for enhanced security
6. **Rate Limiting**: Add rate limiting to prevent brute force attacks 