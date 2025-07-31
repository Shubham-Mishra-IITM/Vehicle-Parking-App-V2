from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from utils.cache_enhanced import cached_endpoint, invalidate_cache, cache_manager

parking_bp = Blueprint('parking', __name__)

def token_required(f):
    """Decorator to require valid authentication token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
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

@parking_bp.route('/lots', methods=['GET'])
@cached_endpoint('parking_lots', timeout=300)
def get_parking_lots():
    """Get all available parking lots (public endpoint) - CACHED"""
    try:
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        
        lots = ParkingLot.query.filter_by(is_active=True).all()
        
        # Add availability information with optimized queries
        lots_data = []
        for lot in lots:
            lot_data = lot.to_dict()
            
            # Check cache for available spots count first
            cache_key = f'spots:lot_{lot.id}:available'
            available_spots = cache_manager.get(cache_key)
            
            if available_spots is None:
                # Calculate and cache available spots
                available_spots = ParkingSpot.query.filter_by(
                    lot_id=lot.id, 
                    status='A'
                ).count()
                cache_manager.set(cache_key, available_spots, 60)  # Cache for 1 minute
            
            lot_data['available_spots'] = available_spots
            lots_data.append(lot_data)
        
        return jsonify(lots_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_bp.route('/lots/<int:lot_id>', methods=['GET'])
@cached_endpoint('parking_lot_details', timeout=60)
def get_lot_details(lot_id):
    """Get detailed information about a parking lot - CACHED"""
    try:
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        
        lot = ParkingLot.query.get_or_404(lot_id)
        
        # Get available spots with caching
        cache_key_available = f'spots:lot_{lot_id}:available_details'
        cache_key_occupied = f'spots:lot_{lot_id}:occupied_details'
        
        available_spots_data = cache_manager.get(cache_key_available)
        occupied_spots_data = cache_manager.get(cache_key_occupied)
        
        if available_spots_data is None:
            available_spots = ParkingSpot.query.filter_by(
                lot_id=lot_id,
                status='A',
                is_active=True
            ).all()
            available_spots_data = [spot.to_dict() for spot in available_spots]
            cache_manager.set(cache_key_available, available_spots_data, 60)  # Cache for 1 minute
        
        if occupied_spots_data is None:
            occupied_spots = ParkingSpot.query.filter_by(
                lot_id=lot_id,
                status='O',
                is_active=True
            ).all()
            occupied_spots_data = [spot.to_dict() for spot in occupied_spots]
            cache_manager.set(cache_key_occupied, occupied_spots_data, 60)  # Cache for 1 minute
        
        lot_data = lot.to_dict()
        lot_data['available_spots_details'] = available_spots_data
        lot_data['occupied_spots_details'] = occupied_spots_data
        
        return jsonify(lot_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_bp.route('/reserve', methods=['POST'])
@token_required
def reserve_parking_spot():
    """Reserve a parking spot"""
    try:
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        from models.reservation import Reservation
        from database import db
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['lot_id', 'vehicle_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        lot_id = data['lot_id']
        vehicle_number = data['vehicle_number']
        
        # Check if parking lot exists and is active
        lot = ParkingLot.query.filter_by(id=lot_id, is_active=True).first()
        if not lot:
            return jsonify({'error': 'Parking lot not found or inactive'}), 404
        
        # Find first available spot
        available_spot = ParkingSpot.query.filter_by(
            lot_id=lot_id,
            status='A',
            is_active=True
        ).first()
        
        if not available_spot:
            return jsonify({'error': 'No available parking spots'}), 400
        
        # Check if user already has an active reservation
        active_reservation = Reservation.query.filter_by(
            user_id=request.current_user_id,
            status='active'
        ).first()
        
        if active_reservation:
            return jsonify({
                'error': 'You already have an active reservation',
                'active_reservation': active_reservation.to_dict()
            }), 400
        
        # Create reservation
        reservation = Reservation(
            spot_id=available_spot.id,
            user_id=request.current_user_id,
            vehicle_number=vehicle_number,
            status='active',
            remarks=data.get('remarks')
        )
        
        # Occupy the spot
        available_spot.occupy_spot()
        
        db.session.add(reservation)
        db.session.commit()
        
        # Invalidate cache after successful reservation
        invalidate_cache('reservation_created', lot_id=lot_id, user_id=request.current_user_id)
        
        return jsonify({
            'message': 'Parking spot reserved successfully',
            'reservation': reservation.to_dict(),
            'parking_spot': available_spot.to_dict(),
            'parking_lot': lot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@parking_bp.route('/release/<int:reservation_id>', methods=['PUT'])
@token_required
def release_parking_spot(reservation_id):
    """Release a parking spot"""
    try:
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        from database import db
        
        # Find the reservation
        reservation = Reservation.query.get_or_404(reservation_id)
        
        # Check if the reservation belongs to the current user
        if reservation.user_id != request.current_user_id:
            return jsonify({'error': 'You can only release your own reservations'}), 403
        
        # Check if the reservation is active
        if reservation.status != 'active':
            return jsonify({'error': 'Reservation is not active'}), 400
        
        # Get the parking spot and lot
        parking_spot = ParkingSpot.query.get(reservation.spot_id)
        parking_lot = ParkingLot.query.get(parking_spot.lot_id)
        
        # Complete the reservation
        reservation.complete_reservation(float(parking_lot.price))
        
        # Release the spot
        parking_spot.release_spot()
        
        db.session.commit()
        
        # Invalidate cache after successful release
        invalidate_cache('reservation_updated', 
                        lot_id=parking_lot.id, 
                        user_id=request.current_user_id)
        
        return jsonify({
            'message': 'Parking spot released successfully',
            'reservation': reservation.to_dict(),
            'total_cost': float(reservation.parking_cost)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@parking_bp.route('/my-reservations', methods=['GET'])
@token_required
def get_my_reservations():
    """Get current user's reservations"""
    try:
        from models.reservation import Reservation
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        status = request.args.get('status')
        
        query = Reservation.query.filter_by(user_id=request.current_user_id)
        
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

@parking_bp.route('/active-reservation', methods=['GET'])
@token_required
def get_active_reservation():
    """Get current user's active reservation"""
    try:
        from models.reservation import Reservation
        
        reservation = Reservation.query.filter_by(
            user_id=request.current_user_id,
            status='active'
        ).first()
        
        if reservation:
            return jsonify({
                'active_reservation': reservation.to_dict()
            }), 200
        else:
            return jsonify({
                'active_reservation': None
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
