from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
import csv
import io

user_bp = Blueprint('user', __name__)

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

@user_bp.route('/dashboard', methods=['GET'])
@token_required
def user_dashboard():
    """Get user dashboard data"""
    try:
        from models.reservation import Reservation
        from models.parking_lot import ParkingLot
        from database import db
        from sqlalchemy import func, extract
        
        user_id = request.current_user_id
        
        # Get active reservation
        active_reservation = Reservation.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        # Get statistics
        total_reservations = Reservation.query.filter_by(user_id=user_id).count()
        completed_reservations = Reservation.query.filter_by(
            user_id=user_id,
            status='completed'
        ).count()
        
        # Calculate total spent
        total_spent = db.session.query(
            func.sum(Reservation.parking_cost)
        ).filter_by(
            user_id=user_id,
            status='completed'
        ).scalar() or 0
        
        # Get recent reservations
        recent_reservations = Reservation.query.filter_by(
            user_id=user_id
        ).order_by(
            Reservation.created_at.desc()
        ).limit(5).all()
        
        # Get monthly statistics (last 6 months)
        monthly_stats = []
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_reservations = Reservation.query.filter(
                Reservation.user_id == user_id,
                extract('year', Reservation.created_at) == month_date.year,
                extract('month', Reservation.created_at) == month_date.month
            ).count()
            
            month_spent = db.session.query(
                func.sum(Reservation.parking_cost)
            ).filter(
                Reservation.user_id == user_id,
                Reservation.status == 'completed',
                extract('year', Reservation.created_at) == month_date.year,
                extract('month', Reservation.created_at) == month_date.month
            ).scalar() or 0
            
            monthly_stats.append({
                'month': month_date.strftime('%B %Y'),
                'reservations': month_reservations,
                'amount_spent': float(month_spent)
            })
        
        # Get most used parking lot
        most_used_lot = db.session.query(
            ParkingLot.prime_location_name,
            func.count(Reservation.id).label('usage_count')
        ).join(
            Reservation,
            Reservation.spot_id.in_(
                db.session.query(func.distinct(Reservation.spot_id))
                .join(ParkingLot)
                .filter(Reservation.user_id == user_id)
            )
        ).group_by(
            ParkingLot.id
        ).order_by(
            func.count(Reservation.id).desc()
        ).first()
        
        return jsonify({
            'active_reservation': active_reservation.to_dict() if active_reservation else None,
            'statistics': {
                'total_reservations': total_reservations,
                'completed_reservations': completed_reservations,
                'total_spent': float(total_spent)
            },
            'recent_reservations': [r.to_dict() for r in recent_reservations],
            'monthly_stats': monthly_stats,
            'most_used_lot': {
                'name': most_used_lot[0] if most_used_lot else None,
                'usage_count': most_used_lot[1] if most_used_lot else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile"""
    try:
        from models.user import User
        
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile"""
    try:
        from models.user import User
        from database import db
        
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user.id
            ).first()
            if existing_user:
                return jsonify({'error': 'Email already taken'}), 400
            user.email = data['email']
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/export-csv', methods=['POST'])
@token_required
def export_reservations_csv():
    """Export user's reservations as CSV (async job trigger)"""
    try:
        from tasks.export_csv import generate_user_csv_export
        from models.user import User
        
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Trigger async task
        task = generate_user_csv_export.delay(request.current_user_id)
        
        return jsonify({
            'message': 'CSV export job started',
            'task_id': task.id,
            'status': 'processing'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/export-status/<task_id>', methods=['GET'])
@token_required
def get_export_status(task_id):
    """Get status of CSV export job"""
    try:
        from tasks.export_csv import generate_user_csv_export
        
        task = generate_user_csv_export.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Job is waiting to be processed'
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'status': task.info.get('status', ''),
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1)
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'status': 'Export completed successfully',
                'download_url': task.result.get('download_url'),
                'file_path': task.result.get('file_path')
            }
        else:  # FAILURE
            response = {
                'state': task.state,
                'status': 'Export failed',
                'error': str(task.info)
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/parking-history', methods=['GET'])
@token_required
def get_parking_history():
    """Get detailed parking history with filters"""
    try:
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        from database import db
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        lot_id = request.args.get('lot_id', type=int)
        
        # Build query
        query = db.session.query(Reservation).filter_by(user_id=request.current_user_id)
        
        if status:
            query = query.filter(Reservation.status == status)
        
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Reservation.created_at >= start_date_obj)
        
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Reservation.created_at <= end_date_obj)
        
        if lot_id:
            # Filter by parking lot
            query = query.join(ParkingSpot).filter(
                ParkingSpot.lot_id == lot_id
            )
        
        # Execute query with pagination
        reservations = query.order_by(
            Reservation.created_at.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Enhance reservation data with lot information
        enhanced_reservations = []
        for reservation in reservations.items:
            res_data = reservation.to_dict()
            
            # Add parking lot and spot information
            spot = ParkingSpot.query.get(reservation.spot_id)
            if spot:
                lot = ParkingLot.query.get(spot.lot_id)
                res_data['parking_spot'] = {
                    'spot_number': spot.spot_number,
                    'lot_name': lot.prime_location_name if lot else 'Unknown',
                    'lot_address': lot.address if lot else 'Unknown'
                }
            
            enhanced_reservations.append(res_data)
        
        return jsonify({
            'reservations': enhanced_reservations,
            'total': reservations.total,
            'pages': reservations.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
