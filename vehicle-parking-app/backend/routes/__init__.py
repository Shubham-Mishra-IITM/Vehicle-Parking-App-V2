from flask import Blueprint

def register_routes(app):
    """Register all route blueprints with the Flask app"""
    
    # Import blueprints
    try:
        from .auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        print("✅ Auth routes registered")
    except ImportError as e:
        print(f"⚠️  Auth routes not found: {e}")
    
    try:
        from .admin import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        print("✅ Admin routes registered")
    except ImportError as e:
        print(f"⚠️  Admin routes not found: {e}")
    
    try:
        from .user import user_bp
        app.register_blueprint(user_bp, url_prefix='/api/user')
        print("✅ User routes registered")
    except ImportError as e:
        print(f"⚠️  User routes not found: {e}")
    
    try:
        from .parking import parking_bp
        app.register_blueprint(parking_bp, url_prefix='/api/parking')
        print("✅ Parking routes registered")
    except ImportError as e:
        print(f"⚠️  Parking routes not found: {e}")

# Keep backward compatibility
routes = Blueprint('routes', __name__)