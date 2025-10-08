# Fantasy Betting League - Project Overview & Instructions

## Project Description

A web application that allows users to create custom fantasy betting leagues with friends, place bets with fake currency, and compete for the highest winnings. Think fantasy sports meets custom betting pools for any topic or event.

## Core Features & User Flow

### 1. League Management

- **League Creation**: Users can create leagues with custom themes (e.g., TV shows, sports seasons, general events)
- **Time Management**: Leagues can be time-limited (specific duration) or indefinite
- **Invitation System**: League creators invite friends via links, codes, or direct invitations
- **Permission Management**: Original creator has admin rights, can promote other users to admin status

### 2. User Authentication & Authorization

- User registration and login system
- Role-based permissions (Admin vs Regular Player)
- Profile management with league history and statistics

### 3. Betting System

- **Ticket Creation** (Admin only):
  - Over/Under bets: Betting above or below a specific number
  - Moneyline bets: Choosing between multiple specific outcomes
  - Custom odds setting for each ticket
- **Bet Placement** (All users):
  - Place bets using fake currency allocated upon joining
  - View current bets and potential payouts
  - Bet history and tracking
- **Ticket Resolution** (Admin only):
  - Mark tickets as resolved with final outcomes
  - Automatic payout calculation and distribution

### 4. Currency & Scoring System

- Each player receives starting fake currency when joining a league
- Winnings calculated based on bet amount and odds
- Real-time leaderboard showing current standings
- End-of-league winner determination based on total currency

## Technical Architecture

### Frontend Stack

- **HTML5** with semantic structure
- **Bootstrap** for responsive UI components and grid system
- **CSS3** for custom styling and animations
- **Vanilla JavaScript** for interactivity and API communication

### Backend Stack

- **Flask** (Python web framework)
- **Flask-Login** for session management
- **Flask-WTF** for form handling and CSRF protection
- **Flask-Mail** for email notifications (optional)
- **Bcrypt** for password hashing

### Database

- **MongoDB** as primary database
- **PyMongo** for Python-MongoDB integration

## Database Schema Design

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

### Leagues Collection

```json
{
  "_id": ObjectId,
  "name": "string",
  "description": "string",
  "creator_id": ObjectId,
  "admins": ["user_id_array"],
  "members": [
    {
      "user_id": ObjectId,
      "balance": "number",
      "joined_at": "datetime"
    }
  ],
  "starting_balance": "number",
  "status": "active|completed|paused",
  "created_at": "datetime",
  "end_date": "datetime|null",
  "invite_code": "string"
}
```

### Tickets Collection

```json
{
  "_id": ObjectId,
  "league_id": ObjectId,
  "title": "string",
  "description": "string",
  "type": "over_under|moneyline",
  "options": [
    {
      "option_text": "string",
      "odds": "number"
    }
  ],
  "target_value": "number|null",
  "status": "open|closed|resolved",
  "resolution": "string|null",
  "created_by": ObjectId,
  "created_at": "datetime",
  "closes_at": "datetime",
  "resolved_at": "datetime|null"
}
```

### Bets Collection

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "league_id": ObjectId,
  "ticket_id": ObjectId,
  "amount": "number",
  "selected_option": "string",
  "potential_payout": "number",
  "status": "pending|won|lost",
  "placed_at": "datetime"
}
```

## File Structure

```
fantasy_betting_app/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── models/
│   ├── __init__.py
│   ├── user.py               # User model and operations
│   ├── league.py             # League model and operations
│   ├── ticket.py             # Ticket model and operations
│   └── bet.py                # Bet model and operations
├── routes/
│   ├── __init__.py
│   ├── auth.py               # Authentication routes
│   ├── leagues.py            # League management routes
│   ├── tickets.py            # Ticket creation and resolution
│   └── bets.py               # Betting functionality
├── static/
│   ├── css/
│   │   └── style.css         # Custom styles
│   ├── js/
│   │   ├── main.js           # Core JavaScript functionality
│   │   ├── leagues.js        # League-specific JS
│   │   └── betting.js        # Betting interface JS
└── templates/
    ├── base.html             # Base template with navbar
    ├── index.html            # Homepage
    ├── auth/
    │   ├── login.html
    │   └── register.html
    ├── leagues/
    │   ├── create.html
    │   ├── dashboard.html
    │   └── detail.html
    └── tickets/
        ├── create.html
        └── list.html
```

## Key Features to Implement

### MVP (Minimum Viable Product)

1. User registration and authentication
2. Basic league creation and joining
3. Simple moneyline ticket creation and betting
4. Manual ticket resolution by admins
5. Basic leaderboard display

### Phase 2 Features

1. Over/under betting functionality
2. Advanced league settings (time limits, custom starting balances)
3. Email notifications for bet outcomes
4. Detailed betting history and statistics
5. League invitation system improvements

### Phase 3 Features

1. Real-time updates using WebSockets
2. Mobile-responsive design improvements
3. Advanced analytics and reporting
4. League templates for common betting scenarios
5. Social features (comments, league chat)

## Development Workflow

### Step 1: Environment Setup

- Set up Python virtual environment
- Install required dependencies
- Configure MongoDB connection
- Create basic Flask app structure

### Step 2: Database & Models

- Implement MongoDB connection
- Create data models for Users, Leagues, Tickets, and Bets
- Add basic CRUD operations for each model

### Step 3: Authentication System

- Implement user registration and login
- Add session management
- Create user profile pages

### Step 4: League Management

- Build league creation functionality
- Implement league joining mechanism
- Create league dashboard and member management

### Step 5: Betting System

- Add ticket creation interface for admins
- Implement bet placement functionality
- Create ticket resolution system

### Step 6: Frontend Polish

- Style with Bootstrap and custom CSS
- Add JavaScript for dynamic interactions
- Implement responsive design

### Step 7: Testing & Deployment

- Add error handling and validation
- Test all user flows
- Prepare for deployment

## API Endpoints Structure

### Authentication

- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout

### Leagues

- `GET /leagues` - List user's leagues
- `POST /leagues` - Create new league
- `GET /leagues/<id>` - League details
- `POST /leagues/<id>/join` - Join league
- `PUT /leagues/<id>` - Update league settings

### Tickets

- `GET /leagues/<id>/tickets` - List league tickets
- `POST /leagues/<id>/tickets` - Create new ticket
- `PUT /tickets/<id>/resolve` - Resolve ticket

### Bets

- `POST /tickets/<id>/bet` - Place bet on ticket
- `GET /users/<id>/bets` - User's betting history
