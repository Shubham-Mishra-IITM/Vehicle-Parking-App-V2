from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import jwt
from functools import wraps

# Create blueprint
admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode token
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            from models import User
            user = User.query.get(payload['user_id'])
            if not user or not user.is_admin():
                return jsonify({'error': 'Admin access required'}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/parking-lots', methods=['POST'])
@admin_required
def create_parking_lot():
    """Create a new parking lot"""
    from models import ParkingLot, ParkingSpot, db
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['prime_location_name', 'price', 'address', 'pin_code', 'number_of_spots']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create parking lot
        new_lot = ParkingLot(
            prime_location_name=data['prime_location_name'],
            price=float(data['price']),
            address=data['address'],
            pin_code=data['pin_code'],
            number_of_spots=int(data['number_of_spots']),
            description=data.get('description'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_lot)
        db.session.flush()  # Get the ID
        
        # Create parking spots
        create_parking_spots_for_lot(new_lot)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Parking lot created successfully',
            'parking_lot': new_lot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def create_parking_spots_for_lot(parking_lot):
    """Helper function to create parking spots for a lot"""
    from models import ParkingSpot, db
    
    spots_per_section = 10
    sections = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    spot_count = 0
    for section in sections:
        if spot_count >= parking_lot.number_of_spots:
            break
            
        for spot_num in range(1, spots_per_section + 1):
            if spot_count >= parking_lot.number_of_spots:
                break
                
            spot_number = f"{section}{spot_num}"
            parking_spot = ParkingSpot(
                spot_number=spot_number,
                lot_id=parking_lot.id,
                status='A',  # Available
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(parking_spot)
            spot_count += 1

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    from models import User, ParkingLot, ParkingSpot, Reservation
    
    try:
        # Get basic counts
        total_users = User.query.filter_by(role='user').count()
        total_lots = ParkingLot.query.count()
        total_spots = ParkingSpot.query.count()
        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
        available_spots = ParkingSpot.query.filter_by(status='A').count()
        
        # Get active reservations
        active_reservations = Reservation.query.filter_by(status='active').count()
        completed_reservations = Reservation.query.filter_by(status='completed').count()
        
        # Calculate occupancy rate
        occupancy_rate = (occupied_spots / total_spots * 100) if total_spots > 0 else 0
        
        return jsonify({
            'users': {
                'total': total_users
            },
            'parking_lots': {
                'total': total_lots
            },
            'parking_spots': {
                'total': total_spots,
                'occupied': occupied_spots,
                'available': available_spots,
                'occupancy_rate': round(occupancy_rate, 2)
            },
            'reservations': {
                'active': active_reservations,
                'completed': completed_reservations,
                'total': active_reservations + completed_reservations
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500