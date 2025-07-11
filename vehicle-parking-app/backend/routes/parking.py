from flask import Blueprint

# Create blueprint
parking_bp = Blueprint('parking', __name__)

@parking_bp.route('/lots', methods=['GET'])
def get_parking_lots():
    """Get all parking lots - placeholder"""
    return {'message': 'Parking lots endpoint'}, 200

@parking_bp.route('/spots/<int:lot_id>', methods=['GET'])
def get_parking_spots(lot_id):
    """Get parking spots for a lot - placeholder"""
    return {'message': f'Parking spots for lot {lot_id}'}, 200