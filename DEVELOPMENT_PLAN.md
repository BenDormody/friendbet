# Fantasy Betting League - Development Plan

## Project Overview

A web application for creating custom fantasy betting leagues with friends, featuring fake currency betting, league management, and real-time leaderboards.

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB with PyMongo
- **Frontend**: HTML5, CSS3, Bootstrap, Vanilla JavaScript
- **Authentication**: Flask-Login, Bcrypt
- **Forms**: Flask-WTF with CSRF protection
- **Styling**: Custom dark theme with neon green accents

## Development Phases

### Phase 1: Project Setup & Configuration ✅ IN PROGRESS

- [x] Create project structure
- [ ] Set up virtual environment and dependencies
- [ ] Configure Flask application
- [ ] Set up MongoDB connection
- [ ] Create configuration files

### Phase 2: Database Models & Core Logic

- [ ] User model (authentication, profile management)
- [ ] League model (creation, management, member tracking)
- [ ] Ticket model (betting options, odds, resolution)
- [ ] Bet model (user bets, payouts, history)
- [ ] Database utility functions

### Phase 3: Authentication System

- [ ] User registration with validation
- [ ] Login/logout functionality
- [ ] Session management
- [ ] Password hashing and security
- [ ] User profile pages

### Phase 4: League Management

- [ ] League creation interface
- [ ] League joining via invite codes
- [ ] Member management and permissions
- [ ] League dashboard and settings
- [ ] League invitation system

### Phase 5: Betting System Core

- [ ] Ticket creation (admin only)
- [ ] Moneyline betting options
- [ ] Over/under betting options
- [ ] Bet placement interface
- [ ] Balance management

### Phase 6: Ticket Resolution & Payouts

- [ ] Admin ticket resolution
- [ ] Automatic payout calculation
- [ ] Bet status updates
- [ ] Winner determination

### Phase 7: Frontend & Styling

- [ ] Base HTML templates
- [ ] Dark theme CSS implementation
- [ ] Responsive design
- [ ] Interactive JavaScript features
- [ ] Component styling (cards, buttons, forms)

### Phase 8: Advanced Features

- [ ] Real-time leaderboards
- [ ] Betting history and statistics
- [ ] Email notifications
- [ ] League analytics
- [ ] Mobile optimization

### Phase 9: Testing & Deployment

- [ ] Error handling and validation
- [ ] User flow testing
- [ ] Security testing
- [ ] Performance optimization
- [ ] Deployment preparation

## File Structure

```
fantasy_betting_app/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
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
│   │   ├── base.css          # Base styles and variables
│   │   ├── components.css    # Component-specific styles
│   │   └── pages.css         # Page-specific styles
│   ├── js/
│   │   ├── main.js           # Core JavaScript functionality
│   │   ├── leagues.js        # League-specific JS
│   │   ├── betting.js        # Betting interface JS
│   │   └── utils.js          # Utility functions
│   └── images/
│       └── icons/            # Icon assets
└── templates/
    ├── base.html             # Base template with navbar
    ├── index.html            # Homepage
    ├── auth/
    │   ├── login.html
    │   └── register.html
    ├── leagues/
    │   ├── create.html
    │   ├── dashboard.html
    │   ├── detail.html
    │   └── invite.html
    └── tickets/
        ├── create.html
        ├── list.html
        └── detail.html
```

## Key Features Implementation Order

### MVP Features (Priority 1)

1. User authentication (register/login)
2. Basic league creation and joining
3. Simple moneyline ticket creation
4. Basic bet placement
5. Manual ticket resolution
6. Simple leaderboard

### Phase 2 Features (Priority 2)

1. Over/under betting
2. Advanced league settings
3. Email notifications
4. Detailed betting history
5. Improved invitation system

### Phase 3 Features (Priority 3)

1. Real-time updates
2. Mobile optimization
3. Advanced analytics
4. League templates
5. Social features

## Database Schema Implementation

### Users Collection

```python
{
    "_id": ObjectId,
    "username": str,
    "email": str,
    "password_hash": str,
    "created_at": datetime,
    "leagues": [ObjectId]  # Array of league IDs
}
```

### Leagues Collection

```python
{
    "_id": ObjectId,
    "name": str,
    "description": str,
    "creator_id": ObjectId,
    "admins": [ObjectId],
    "members": [
        {
            "user_id": ObjectId,
            "balance": float,
            "joined_at": datetime
        }
    ],
    "starting_balance": float,
    "status": str,  # "active", "completed", "paused"
    "created_at": datetime,
    "end_date": datetime,
    "invite_code": str
}
```

### Tickets Collection

```python
{
    "_id": ObjectId,
    "league_id": ObjectId,
    "title": str,
    "description": str,
    "type": str,  # "over_under", "moneyline"
    "options": [
        {
            "option_text": str,
            "odds": float
        }
    ],
    "target_value": float,  # For over/under
    "status": str,  # "open", "closed", "resolved"
    "resolution": str,
    "created_by": ObjectId,
    "created_at": datetime,
    "closes_at": datetime,
    "resolved_at": datetime
}
```

### Bets Collection

```python
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "league_id": ObjectId,
    "ticket_id": ObjectId,
    "amount": float,
    "selected_option": str,
    "potential_payout": float,
    "status": str,  # "pending", "won", "lost"
    "placed_at": datetime
}
```

## API Endpoints Structure

### Authentication

- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /profile` - User profile

### Leagues

- `GET /leagues` - List user's leagues
- `POST /leagues` - Create new league
- `GET /leagues/<id>` - League details
- `POST /leagues/<id>/join` - Join league with code
- `PUT /leagues/<id>` - Update league settings
- `GET /leagues/<id>/leaderboard` - League leaderboard

### Tickets

- `GET /leagues/<id>/tickets` - List league tickets
- `POST /leagues/<id>/tickets` - Create new ticket (admin)
- `GET /tickets/<id>` - Ticket details
- `PUT /tickets/<id>/resolve` - Resolve ticket (admin)

### Bets

- `POST /tickets/<id>/bet` - Place bet on ticket
- `GET /users/<id>/bets` - User's betting history
- `GET /leagues/<id>/bets` - League betting activity

## Styling Implementation Plan

### CSS Architecture

1. **Base Styles** (`base.css`)

   - CSS custom properties (variables)
   - Reset/normalize styles
   - Typography scale
   - Color palette

2. **Component Styles** (`components.css`)

   - Buttons (primary, secondary, ghost, icon)
   - Cards (base, balance, ticket, league)
   - Forms (inputs, selects, labels)
   - Navigation (top bar, category scroll)
   - Badges and status indicators

3. **Page Styles** (`pages.css`)
   - Homepage layout
   - Authentication pages
   - League dashboard
   - League detail pages
   - Betting interface

### Key Design Elements

- Dark theme with neon green (#c4ff0d) accents
- Card-based modular layout
- High contrast for readability
- Smooth animations and transitions
- Responsive design for mobile/tablet
- Sports betting platform aesthetic

## Security Considerations

- Password hashing with bcrypt
- CSRF protection on forms
- Input validation and sanitization
- Session security
- Rate limiting on API endpoints
- MongoDB injection prevention

## Testing Strategy

- Unit tests for models and utilities
- Integration tests for API endpoints
- User flow testing
- Security testing
- Performance testing
- Cross-browser compatibility

## Deployment Checklist

- Environment configuration
- Database setup and migrations
- Static file serving
- Error logging and monitoring
- SSL certificate setup
- Domain configuration
- Performance optimization

---

**Current Status**: Phase 7 - Frontend Templates (In Progress)
**Last Updated**: [Current Date]
**Next Milestone**: Complete remaining templates and static assets

## Progress Update

### ✅ Completed Phases

- **Phase 1**: Project Setup & Configuration
- **Phase 2**: Database Models & Core Logic
- **Phase 3**: Authentication System
- **Phase 4**: League Management
- **Phase 5**: Betting System Core
- **Phase 6**: Ticket Resolution & Payouts

### 🔄 Currently Working On

- **Phase 7**: Frontend & Styling
  - ✅ Base HTML template with navigation
  - ✅ Authentication templates (login/register)
  - ✅ Homepage with hero section and features
  - ✅ League dashboard template
  - 🔄 League detail and creation templates
  - 🔄 Ticket and betting interface templates

### 📋 Remaining Tasks

- Complete remaining HTML templates
- Finish CSS styling and responsive design
- Implement JavaScript functionality
- Add error handling and validation
- Testing and deployment preparation
