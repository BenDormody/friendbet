from flask import Flask, render_template, redirect, url_for
from flask_login import login_required, current_user
from config import Config
from models import login_manager
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
        if current_user.is_authenticated:
            return redirect(url_for('leagues.dashboard'))
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
