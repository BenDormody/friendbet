# Fantasy Betting League

A web application that allows users to create custom fantasy betting leagues with friends, place bets with fake currency, and compete for the highest winnings.

## 🎯 Features

### Core Functionality

- **User Authentication**: Secure registration, login, and session management
- **League Management**: Create private leagues, invite friends, manage permissions
- **Betting System**: Place moneyline and over/under bets with custom odds
- **Real-time Leaderboards**: Track standings and performance
- **Ticket Resolution**: Admins can resolve tickets and distribute winnings

### League Features

- Custom league themes and descriptions
- Invite codes for easy joining
- Admin permissions and member management
- Flexible duration (time-limited or indefinite)
- Starting balance configuration

### Betting Features

- Moneyline betting (multiple options)
- Over/Under betting with target values
- Custom odds setting by admins
- Real-time balance tracking
- Betting history and statistics

## 🛠 Technology Stack

### Backend

- **Flask** - Python web framework
- **MongoDB** - NoSQL database with PyMongo
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and CSRF protection
- **Bcrypt** - Password hashing

### Frontend

- **HTML5** - Semantic markup
- **CSS3** - Custom dark theme styling
- **Bootstrap 5** - Responsive UI components
- **Vanilla JavaScript** - Interactive features
- **Lucide Icons** - Modern iconography

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd fantasy-betting-league
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MongoDB connection**

   ```bash
   # Option 1: Use the configuration helper
   python configure_mongodb.py

   # Option 2: Manually edit .env file
   # Replace MONGODB_URI with your connection string
   ```

5. **Start MongoDB** (if using local MongoDB)

   ```bash
   # Make sure MongoDB is running on localhost:27017
   # Skip this step if using remote MongoDB (Atlas, etc.)
   ```

6. **Run the application**

   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Register a new account or login
   - Create your first league!

## 📁 Project Structure

```
fantasy_betting_app/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── database.py                 # Database connection manager
├── requirements.txt            # Python dependencies
├── models/                     # Data models
│   ├── __init__.py
│   ├── user.py                # User model and operations
│   ├── league.py              # League model and operations
│   ├── ticket.py              # Ticket model and operations
│   └── bet.py                 # Bet model and operations
├── routes/                     # Application routes
│   ├── __init__.py
│   ├── auth.py                # Authentication routes
│   ├── leagues.py             # League management routes
│   ├── tickets.py             # Ticket creation and resolution
│   └── bets.py                # Betting functionality
├── static/                     # Static assets
│   ├── css/
│   │   ├── base.css           # Base styles and variables
│   │   ├── components.css     # Component-specific styles
│   │   └── pages.css          # Page-specific styles
│   ├── js/
│   │   ├── main.js            # Core JavaScript functionality
│   │   ├── leagues.js         # League-specific JS
│   │   ├── betting.js         # Betting interface JS
│   │   └── utils.js           # Utility functions
│   └── images/                # Image assets
└── templates/                  # HTML templates
    ├── base.html              # Base template with navigation
    ├── index.html             # Homepage
    ├── auth/                  # Authentication pages
    ├── leagues/               # League management pages
    └── tickets/               # Ticket and betting pages
```

## 🎨 Design System

### Color Palette

- **Primary Background**: `#0a0a0a` (Deep black)
- **Secondary Background**: `#1a1a1a` (Dark gray)
- **Card Background**: `#1e1e1e` (Lighter gray)
- **Accent Color**: `#c4ff0d` (Neon green)
- **Text Primary**: `#ffffff` (White)
- **Text Secondary**: `#a0a0a0` (Light gray)

### Typography

- **Primary Font**: Inter (Clean, modern sans-serif)
- **Display Font**: Bebas Neue (Bold, impactful headings)
- **Monospace**: Roboto Mono (Code and data)

### Components

- **Cards**: Rounded corners with subtle shadows
- **Buttons**: Pill-shaped with hover animations
- **Forms**: Dark theme with neon green focus states
- **Navigation**: Sticky header with smooth transitions

## 🔧 Configuration

### Environment Variables

```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/fantasy_betting
# For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/fantasy_betting
# For remote server: mongodb://username:password@your-server.com:27017/fantasy_betting

# MongoDB Connection Settings (Optional)
MONGODB_CONNECT_TIMEOUT_MS=10000
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
MONGODB_SOCKET_TIMEOUT_MS=20000

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Database Configuration

The application uses MongoDB with the following collections:

- `users` - User accounts and profiles
- `leagues` - League information and members
- `tickets` - Betting tickets and options
- `bets` - User bets and outcomes

#### MongoDB Connection Options

**1. MongoDB Atlas (Recommended)**

- Free cloud-hosted MongoDB
- Easy setup and scaling
- Automatic backups and security
- Connection string format: `mongodb+srv://username:password@cluster.mongodb.net/fantasy_betting`

**2. Remote MongoDB Server**

- Your own MongoDB server
- Full control over configuration
- Connection string format: `mongodb://username:password@your-server.com:27017/fantasy_betting`

**3. Local MongoDB**

- For development and testing
- Requires MongoDB installation
- Connection string format: `mongodb://localhost:27017/fantasy_betting`

#### Quick Setup

Use the built-in configuration helper:

```bash
python configure_mongodb.py
```

This will guide you through setting up your MongoDB connection.

## 📱 Features Overview

### User Authentication

- Secure registration with email validation
- Password hashing with bcrypt
- Session management with Flask-Login
- Real-time username/email availability checking

### League Management

- Create leagues with custom settings
- Invite friends with shareable codes
- Admin permissions and member management
- Flexible starting balances and duration

### Betting System

- **Moneyline Bets**: Choose between multiple options
- **Over/Under Bets**: Bet above or below a target value
- Real-time balance updates
- Automatic payout calculation

### Admin Features

- Create and manage betting tickets
- Set custom odds for each option
- Resolve tickets with winning outcomes
- Automatic bet resolution and balance updates

## 🚀 Deployment

### Production Setup

1. Set `FLASK_ENV=production` in environment variables
2. Configure MongoDB Atlas or production MongoDB instance
3. Set up email service for notifications
4. Configure reverse proxy (nginx/Apache)
5. Set up SSL certificate
6. Configure domain and DNS

### Docker Deployment

```bash
# Build Docker image
docker build -t fantasy-betting-league .

# Run container
docker run -p 5000:5000 --env-file .env fantasy-betting-league
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Development Plan](DEVELOPMENT_PLAN.md) for current status
2. Review the [Troubleshooting Guide](TROUBLESHOOTING.md)
3. Open an issue on GitHub
4. Contact the development team

## 🎯 Roadmap

### Phase 2 Features (Coming Soon)

- Email notifications for bet outcomes
- Advanced league analytics
- Mobile app development
- Real-time WebSocket updates

### Phase 3 Features (Future)

- Social features (comments, chat)
- League templates
- Advanced betting options
- Tournament brackets

---

**Built with ❤️ for the fantasy betting community**
