from flask import Blueprint
from .auth import auth_bp
from .admin import admin_bp
from .analytics import analytics_bp
from .parking import parking_bp
from .user import user_bp

def register_routes(app):
    """Register all route blueprints"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(analytics_bp, url_prefix='/api')  # Analytics routes include /admin/analytics
    app.register_blueprint(parking_bp, url_prefix='/api/parking')
    app.register_blueprint(user_bp, url_prefix='/api/user')
