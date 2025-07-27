# Fantasy Betting League

A web application that allows users to create custom fantasy betting leagues with friends, place bets with fake currency, and compete for the highest winnings. Think fantasy sports meets custom betting pools for any topic or event.

## Features

### Core Features

- **League Management**: Create and join custom betting leagues
- **User Authentication**: Secure registration and login system
- **Betting System**: Place bets on moneyline and over/under tickets
- **Currency Management**: Fake currency system with starting balances
- **Leaderboards**: Real-time standings and statistics
- **Admin Controls**: League creators can manage tickets and resolve bets

### Betting Types

- **Moneyline Bets**: Choose between multiple specific outcomes
- **Over/Under Bets**: Bet above or below a specific number
- **Custom Odds**: Admins can set custom odds for each option

## Technology Stack

### Backend

- **Flask**: Python web framework
- **Flask-Login**: Session management
- **Flask-WTF**: Form handling and CSRF protection
- **PyMongo**: MongoDB integration
- **Bcrypt**: Password hashing

### Frontend

- **Bootstrap 5**: Responsive UI framework
- **Vanilla JavaScript**: Interactive functionality
- **HTML5/CSS3**: Modern web standards

### Database

- **MongoDB**: NoSQL database for flexible data storage

## Development Setup

### Prerequisites

- Docker and Docker Compose
- VS Code with Dev Containers extension (recommended)

### Quick Start with Dev Containers

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd friendbet
   ```

2. **Open in Dev Container**

   - Open VS Code
   - Install the "Dev Containers" extension if not already installed
   - Open the project folder
   - When prompted, click "Reopen in Container"
   - Wait for the container to build and start

3. **Environment Setup**
   The dev container will automatically:

   - Install Python dependencies
   - Start MongoDB service
   - Configure the development environment

4. **Run the Application**

   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5050`

### Manual Setup (Alternative)

1. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MongoDB**

   - Install MongoDB locally or use Docker
   - Create a database named `fantasy_betting`

3. **Environment Variables**
   Create a `.env` file in the project root:

   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   MONGODB_URI=mongodb://localhost:27018/fantasy_betting
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

## Project Structure

```
friendbet/
├── .devcontainer/          # Development container configuration
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   └── Dockerfile
├── models/                 # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── league.py
│   ├── ticket.py
│   └── bet.py
├── routes/                 # Flask route blueprints
│   ├── __init__.py
│   ├── auth.py
│   ├── leagues.py
│   ├── tickets.py
│   └── bets.py
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   └── ...
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## API Endpoints

### Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Leagues

- `GET /leagues/` - User's league dashboard
- `POST /leagues/create` - Create new league
- `GET /leagues/<id>` - League details
- `POST /leagues/<id>/join` - Join league

### Tickets

- `GET /tickets/league/<id>` - List league tickets
- `POST /tickets/league/<id>/create` - Create new ticket
- `GET /tickets/<id>` - View ticket details
- `POST /tickets/<id>/resolve` - Resolve ticket

### Bets

- `POST /bets/place/<ticket_id>` - Place bet
- `GET /bets/history` - User's betting history
- `GET /bets/stats` - User's betting statistics

## Development Workflow

### Phase 1: MVP (Current)

- [x] User authentication system
- [x] Basic league creation and management
- [x] Simple moneyline betting
- [x] Manual ticket resolution
- [x] Basic leaderboard

### Phase 2: Enhanced Features

- [ ] Over/under betting functionality
- [ ] Advanced league settings
- [ ] Email notifications
- [ ] Detailed statistics
- [ ] Improved invitation system

### Phase 3: Advanced Features

- [ ] Real-time updates with WebSockets
- [ ] Mobile-responsive improvements
- [ ] Advanced analytics
- [ ] League templates
- [ ] Social features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository.
