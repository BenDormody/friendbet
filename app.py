from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user, login_user, logout_user
from config import Config
from auth import login_manager
from models.user import User
from routes import init_app as init_routes


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Register blueprints
    init_routes(app)

    # Main routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    # Authentication API endpoints
    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Check if user already exists
        if User.get_by_username(username):
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.get_by_email(email):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
            
            return jsonify({
                'message': 'Registration successful! Please log in.',
                'user': {
                    'id': str(user._id),
                    'username': user.username,
                    'email': user.email
                }
            }), 201
        except Exception as e:
            return jsonify({'error': 'Registration failed. Please try again.'}), 500

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Try to find user by email first, then by username
        user = User.get_by_email(email)
        if not user:
            user = User.get_by_username(email)
        
        if user and user.check_password(password):
            login_user(user)
            return jsonify({
                'message': 'Login successful!',
                'user': {
                    'id': str(user._id),
                    'username': user.username,
                    'email': user.email
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid email/username or password'}), 401

    @app.route('/api/auth/logout', methods=['POST'])
    @login_required
    def api_logout():
        logout_user()
        return jsonify({'message': 'Logout successful!'}), 200

    @app.route('/api/auth/check')
    def api_check_auth():
        if current_user.is_authenticated:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': str(current_user._id),
                    'username': current_user.username,
                    'email': current_user.email
                }
            }), 200
        else:
            return jsonify({'authenticated': False}), 401

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    return app


app = create_app()

if __name__ == '__main__':
    try:
        print("Starting Fantasy Betting League application...")
        print("Server will be available at: http://localhost:5001")
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Trying alternative port 5002...")
        try:
            app.run(debug=True, host='0.0.0.0', port=5002)
        except Exception as e2:
            print(f"Error starting server on port 5002: {e2}")
            print("Please check if any other applications are using these ports.")
