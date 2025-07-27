from flask import Blueprint
from .auth import auth_bp
from .leagues import leagues_bp
from .tickets import tickets_bp
from .bets import bets_bp


def init_app(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(leagues_bp, url_prefix='/leagues')
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(bets_bp, url_prefix='/bets')
