from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            if payload.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
                
            request.current_user_id = payload['user_id']
            request.current_user_role = payload['role']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    """Get admin dashboard data"""
    try:
        from models.user import User
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        from models.reservation import Reservation
        from database import db
        
        # Get statistics
        total_users = User.query.filter_by(role='user').count()
        total_parking_lots = ParkingLot.query.filter_by(is_active=True).count()
        total_spots = ParkingSpot.query.filter_by(is_active=True).count()
        occupied_spots = ParkingSpot.query.filter_by(status='O', is_active=True).count()
        available_spots = total_spots - occupied_spots
        
        active_reservations = Reservation.query.filter_by(status='active').count()
        
        # Get recent reservations
        recent_reservations = Reservation.query.order_by(
            Reservation.created_at.desc()
        ).limit(10).all()
        
        # Get parking lots with their statistics
        parking_lots = []
        for lot in ParkingLot.query.filter_by(is_active=True).all():
            lot_data = lot.to_dict()
            parking_lots.append(lot_data)
        
        return jsonify({
            'statistics': {
                'total_users': total_users,
                'total_parking_lots': total_parking_lots,
                'total_spots': total_spots,
                'occupied_spots': occupied_spots,
                'available_spots': available_spots,
                'active_reservations': active_reservations
            },
            'recent_reservations': [r.to_dict() for r in recent_reservations],
            'parking_lots': parking_lots
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots', methods=['GET'])
@admin_required
def get_parking_lots():
    """Get all parking lots"""
    try:
        from models.parking_lot import ParkingLot
        
        lots = ParkingLot.query.all()
        return jsonify([lot.to_dict() for lot in lots]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots', methods=['POST'])
@admin_required
def create_parking_lot():
    """Create a new parking lot"""
    try:
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        from database import db
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['prime_location_name', 'price', 'address', 'pin_code', 'number_of_spots']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create parking lot
        parking_lot = ParkingLot(
            prime_location_name=data['prime_location_name'],
            price=data['price'],
            address=data['address'],
            pin_code=data['pin_code'],
            number_of_spots=data['number_of_spots'],
            description=data.get('description'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        db.session.add(parking_lot)
        db.session.flush()  # Get the ID
        
        # Create parking spots
        for i in range(1, int(data['number_of_spots']) + 1):
            spot = ParkingSpot(
                spot_number=f"P{i:03d}",  # P001, P002, etc.
                lot_id=parking_lot.id,
                status='A'
            )
            db.session.add(spot)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Parking lot created successfully',
            'parking_lot': parking_lot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['PUT'])
@admin_required
def update_parking_lot(lot_id):
    """Update a parking lot"""
    try:
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        from database import db
        
        lot = ParkingLot.query.get_or_404(lot_id)
        data = request.get_json()
        
        # Update basic fields
        if 'prime_location_name' in data:
            lot.prime_location_name = data['prime_location_name']
        if 'price' in data:
            lot.price = data['price']
        if 'address' in data:
            lot.address = data['address']
        if 'pin_code' in data:
            lot.pin_code = data['pin_code']
        if 'description' in data:
            lot.description = data['description']
        if 'latitude' in data:
            lot.latitude = data['latitude']
        if 'longitude' in data:
            lot.longitude = data['longitude']
        
        # Handle number of spots change
        if 'number_of_spots' in data:
            new_spot_count = int(data['number_of_spots'])
            current_spot_count = lot.number_of_spots
            
            if new_spot_count > current_spot_count:
                # Add new spots
                for i in range(current_spot_count + 1, new_spot_count + 1):
                    spot = ParkingSpot(
                        spot_number=f"P{i:03d}",
                        lot_id=lot.id,
                        status='A'
                    )
                    db.session.add(spot)
            elif new_spot_count < current_spot_count:
                # Remove spots (only if they're not occupied)
                spots_to_remove = ParkingSpot.query.filter_by(
                    lot_id=lot.id
                ).order_by(ParkingSpot.id.desc()).limit(
                    current_spot_count - new_spot_count
                ).all()
                
                for spot in spots_to_remove:
                    if spot.status == 'O':
                        return jsonify({
                            'error': f'Cannot remove spot {spot.spot_number} as it is occupied'
                        }), 400
                    db.session.delete(spot)
            
            lot.number_of_spots = new_spot_count
        
        db.session.commit()
        
        return jsonify({
            'message': 'Parking lot updated successfully',
            'parking_lot': lot.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots/<int:lot_id>', methods=['DELETE'])
@admin_required
def delete_parking_lot(lot_id):
    """Delete a parking lot (only if all spots are empty)"""
    try:
        from models.parking_lot import ParkingLot
        from database import db
        
        lot = ParkingLot.query.get_or_404(lot_id)
        
        if not lot.can_be_deleted():
            return jsonify({
                'error': 'Cannot delete parking lot with occupied spots'
            }), 400
        
        db.session.delete(lot)
        db.session.commit()
        
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots/<int:lot_id>/spots', methods=['GET'])
@admin_required
def get_parking_spots(lot_id):
    """Get all parking spots for a parking lot"""
    try:
        from models.parking_spot import ParkingSpot
        
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        return jsonify([spot.to_dict() for spot in spots]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all registered users"""
    try:
        from models.user import User
        
        users = User.query.filter_by(role='user').all()
        return jsonify([user.to_dict() for user in users]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reservations', methods=['GET'])
@admin_required
def get_all_reservations():
    """Get all reservations"""
    try:
        from models.reservation import Reservation
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        status = request.args.get('status')
        
        query = Reservation.query
        
        if status:
            query = query.filter_by(status=status)
        
        reservations = query.order_by(
            Reservation.created_at.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'reservations': [r.to_dict() for r in reservations.items],
            'total': reservations.total,
            'pages': reservations.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
