from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from config import config
from database import db
import os


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])

    # Initialize database
    db.init_app(app)

    # Initialize extensions
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.get_by_id(user_id)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.leagues import leagues_bp
    from routes.tickets import tickets_bp
    from routes.bets import bets_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(leagues_bp, url_prefix='/leagues')
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(bets_bp, url_prefix='/bets')

    # Main routes
    @app.route('/')
    def index():
        """Homepage"""
        if current_user.is_authenticated:
            return redirect(url_for('leagues.dashboard'))
        return render_template('index.html')

    @app.route('/about')
    def about():
        """About page"""
        return render_template('about.html')

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    # Template filters
    @app.template_filter('currency')
    def currency_filter(value):
        """Format currency values"""
        return f"${value:,.2f}"

    @app.template_filter('datetime')
    def datetime_filter(value):
        """Format datetime values"""
        if value:
            return value.strftime('%B %d, %Y at %I:%M %p')
        return 'N/A'

    # Context processors
    @app.context_processor
    def inject_user():
        """Make current_user available in all templates"""
        return dict(current_user=current_user)

    return app


# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
