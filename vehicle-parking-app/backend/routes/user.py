from flask import Blueprint

# Create blueprint
user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile - placeholder"""
    return {'message': 'User profile endpoint'}, 200

@user_bp.route('/reservations', methods=['GET'])
def get_reservations():
    """Get user reservations - placeholder"""
    return {'message': 'User reservations endpoint'}, 200