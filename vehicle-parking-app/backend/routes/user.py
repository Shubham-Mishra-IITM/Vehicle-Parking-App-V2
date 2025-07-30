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
        
        # Get status distribution for pie chart
        status_distribution = db.session.query(
            Reservation.status,
            func.count(Reservation.id).label('count')
        ).filter_by(user_id=user_id).group_by(Reservation.status).all()
        
        # Get parking lot usage statistics for bar chart
        lot_usage_stats = db.session.query(
            ParkingLot.prime_location_name,
            func.count(Reservation.id).label('reservations'),
            func.sum(Reservation.parking_cost).label('total_spent')
        ).join(
            Reservation,
            Reservation.spot_id.in_(
                db.session.query(Reservation.spot_id).filter(
                    Reservation.user_id == user_id
                )
            )
        ).group_by(ParkingLot.id).limit(5).all()
        
        # Get weekly activity for the last 4 weeks
        weekly_stats = []
        for i in range(4):
            week_start = datetime.now() - timedelta(days=7*(i+1))
            week_end = datetime.now() - timedelta(days=7*i)
            
            weekly_reservations = Reservation.query.filter(
                Reservation.user_id == user_id,
                Reservation.created_at >= week_start,
                Reservation.created_at < week_end
            ).count()
            
            weekly_spent = db.session.query(
                func.sum(Reservation.parking_cost)
            ).filter(
                Reservation.user_id == user_id,
                Reservation.status == 'completed',
                Reservation.created_at >= week_start,
                Reservation.created_at < week_end
            ).scalar() or 0
            
            weekly_stats.append({
                'week': f"Week {4-i}",
                'week_start': week_start.strftime('%Y-%m-%d'),
                'reservations': weekly_reservations,
                'amount_spent': float(weekly_spent)
            })
        
        return jsonify({
            'active_reservation': active_reservation.to_dict() if active_reservation else None,
            'statistics': {
                'total_reservations': total_reservations,
                'completed_reservations': completed_reservations,
                'total_spent': float(total_spent)
            },
            'recent_reservations': [r.to_dict() for r in recent_reservations],
            'monthly_stats': monthly_stats,
            'weekly_stats': weekly_stats,
            'status_distribution': [
                {'status': status, 'count': count} 
                for status, count in status_distribution
            ],
            'lot_usage_stats': [
                {
                    'lot_name': lot_name, 
                    'reservations': reservations,
                    'total_spent': float(total_spent or 0)
                }
                for lot_name, reservations, total_spent in lot_usage_stats
            ],
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
        if 'username' in data and data['username']:
            # Check if username is already taken by another user
            existing_user = User.query.filter(
                User.username == data['username'],
                User.id != user.id
            ).first()
            if existing_user:
                return jsonify({'error': 'Username already taken'}), 400
            user.username = data['username']
        
        if 'full_name' in data:
            user.full_name = data['full_name']
        
        if 'email' in data and data['email']:
            # Check if email is already taken by another user
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user.id
            ).first()
            if existing_user:
                return jsonify({'error': 'Email already taken'}), 400
            user.email = data['email']
        
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        
        if 'address' in data:
            user.address = data['address']
        
        if 'pin_code' in data:
            user.pin_code = data['pin_code']
        
        # Update timestamp
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password():
    """Change user password"""
    try:
        from models.user import User
        from database import db
        
        user = User.query.get(request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password'):
            return jsonify({'error': 'Current password is required'}), 400
        
        if not data.get('new_password'):
            return jsonify({'error': 'New password is required'}), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(data['new_password']) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        # Update password
        user.set_password(data['new_password'])
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
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

@user_bp.route('/reservations', methods=['POST'])
@token_required
def create_reservation():
    """Create a new parking reservation - automatically assigns first available spot"""
    try:
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        from database import db
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['parking_lot_id', 'vehicle_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        lot_id = data['parking_lot_id']
        vehicle_number = data['vehicle_number']
        
        # Check if parking lot exists and is active
        lot = ParkingLot.query.filter_by(id=lot_id, is_active=True).first()
        if not lot:
            return jsonify({'error': 'Parking lot not found or inactive'}), 404
        
        # Find first available spot (user cannot select specific spot)
        # Use a more robust query that considers both spot status and existing reservations
        from sqlalchemy import and_, not_, exists
        
        available_spot = db.session.query(ParkingSpot).filter(
            and_(
                ParkingSpot.lot_id == lot_id,
                ParkingSpot.status == 'A',  # A = Available
                ParkingSpot.is_active == True,
                # Ensure no active or reserved reservations exist for this spot
                not_(exists().where(
                    and_(
                        Reservation.spot_id == ParkingSpot.id,
                        Reservation.status.in_(['reserved', 'active'])
                    )
                ))
            )
        ).first()
        
        if not available_spot:
            return jsonify({'error': 'No available parking spots in this lot'}), 400
        
        # Calculate cost (default 1 hour if not specified)
        parking_duration = data.get('parking_duration', 1)
        total_cost = lot.price * parking_duration
        
        # Create reservation with 'reserved' status (not yet parked)
        reservation = Reservation(
            spot_id=available_spot.id,
            user_id=request.current_user_id,
            vehicle_number=vehicle_number,
            parking_cost=total_cost,
            status='reserved',  # New status: reserved but not yet parked
            remarks=data.get('remarks')
        )
        
        print(f"DEBUG: Creating reservation for user {request.current_user_id}, spot {available_spot.id}")
        print(f"DEBUG: Spot current status: {available_spot.status}")
        
        # Mark spot as reserved (not yet occupied)
        available_spot.status = 'R'  # R = Reserved
        
        print(f"DEBUG: Updated spot {available_spot.id} status to: {available_spot.status}")
        
        db.session.add(reservation)
        db.session.commit()
        
        print(f"DEBUG: Reservation created successfully with ID: {reservation.id}")
        
        return jsonify({
            'message': 'Parking spot reserved successfully. Please mark as occupied when you park.',
            'reservation': reservation.to_dict(),
            'parking_spot': available_spot.to_dict(),
            'parking_lot': lot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reservations/<int:reservation_id>/park', methods=['PUT'])
@token_required
def mark_as_parked(reservation_id):
    """Mark reservation as parked (user has arrived and parked)"""
    try:
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from database import db
        from datetime import datetime
        
        # Find the reservation
        reservation = Reservation.query.filter_by(
            id=reservation_id,
            user_id=request.current_user_id
        ).first()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        if reservation.status not in ['reserved']:
            return jsonify({'error': 'Reservation cannot be marked as parked'}), 400
        
        # Update reservation status and parking timestamp
        reservation.status = 'active'
        reservation.parking_timestamp = datetime.utcnow()
        
        # Update parking spot status to occupied
        spot = ParkingSpot.query.get(reservation.spot_id)
        if spot:
            spot.status = 'O'  # O = Occupied
        
        db.session.commit()
        
        return jsonify({
            'message': 'Parking marked as occupied successfully',
            'reservation': reservation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reservations/<int:reservation_id>/release', methods=['PUT'])
@token_required
def mark_as_released(reservation_id):
    """Mark parking as released (user has left)"""
    try:
        print(f"DEBUG: Release endpoint called for reservation {reservation_id}")
        print(f"DEBUG: User ID: {request.current_user_id}")
        
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        from database import db
        from datetime import datetime
        
        # Find the reservation
        reservation = Reservation.query.filter_by(
            id=reservation_id,
            user_id=request.current_user_id,
            status='active'
        ).first()
        
        print(f"DEBUG: Found reservation: {reservation}")
        
        if not reservation:
            print(f"DEBUG: No active reservation found for ID {reservation_id} and user {request.current_user_id}")
            return jsonify({'error': 'Active reservation not found'}), 404
        
        print(f"DEBUG: Current reservation status: {reservation.status}")
        print(f"DEBUG: Parking timestamp: {reservation.parking_timestamp}")
        
        # Set leaving timestamp and calculate final cost
        reservation.leaving_timestamp = datetime.utcnow()
        
        # Calculate actual duration and cost
        if reservation.parking_timestamp:
            duration = reservation.leaving_timestamp - reservation.parking_timestamp
            actual_hours = duration.total_seconds() / 3600
            reservation.total_hours = round(actual_hours, 2)
            
            print(f"DEBUG: Calculated actual hours: {actual_hours}")
            
            # Get hourly rate
            spot = ParkingSpot.query.get(reservation.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            
            print(f"DEBUG: Spot: {spot}, Lot: {lot}")
            print(f"DEBUG: Hourly rate: {lot.price}")
            
            # Calculate final cost (minimum 1 hour)
            billable_hours = max(1, actual_hours)
            reservation.parking_cost = round(billable_hours * float(lot.price), 2)
            
            print(f"DEBUG: Billable hours: {billable_hours}, Final cost: {reservation.parking_cost}")
        
        # Complete the reservation
        reservation.status = 'completed'
        
        # Release the parking spot
        spot = ParkingSpot.query.get(reservation.spot_id)
        if spot:
            print(f"DEBUG: Releasing spot {spot.id}, current status: {spot.status}")
            spot.status = 'A'  # A = Available
        
        print("DEBUG: About to commit to database")
        db.session.commit()
        print("DEBUG: Database commit successful")
        
        return jsonify({
            'message': 'Parking released successfully',
            'reservation': reservation.to_dict(),
            'total_duration_hours': reservation.total_hours,
            'final_cost': reservation.parking_cost
        }), 200
        
    except Exception as e:
        print(f"DEBUG: Exception in release endpoint: {str(e)}")
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@token_required
def cancel_reservation(reservation_id):
    """Cancel a user's reservation"""
    try:
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from database import db
        
        # Find the reservation
        reservation = Reservation.query.filter_by(
            id=reservation_id,
            user_id=request.current_user_id
        ).first()
        
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        # Can only cancel reservations that are 'reserved' or 'active' (not completed/cancelled)
        if reservation.status not in ['reserved', 'active']:
            return jsonify({'error': 'Only active or reserved reservations can be cancelled'}), 400
        
        # Free up the parking spot
        spot = ParkingSpot.query.get(reservation.spot_id)
        if spot:
            spot.status = 'A'  # Mark as available
            print(f"DEBUG: Cancelling reservation {reservation_id}, freeing spot {spot.id}")
        
        # Update reservation status
        reservation.status = 'cancelled'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reservation cancelled successfully',
            'reservation': reservation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reservations/<int:reservation_id>/extend', methods=['PUT'])
@token_required
def extend_reservation(reservation_id):
    """Extend a user's reservation"""
    try:
        from models.reservation import Reservation
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        from database import db
        
        data = request.get_json()
        additional_hours = data.get('additional_hours', 1)
        
        # Find the reservation
        reservation = Reservation.query.filter_by(
            id=reservation_id,
            user_id=request.current_user_id,
            status='active'
        ).first()
        
        if not reservation:
            return jsonify({'error': 'Active reservation not found'}), 404
        
        # Get parking lot for pricing
        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        
        additional_cost = lot.price * additional_hours
        
        # Update reservation - extend the cost for additional hours
        # Note: The actual duration is calculated dynamically based on timestamps
        reservation.parking_cost = (reservation.parking_cost or 0) + additional_cost
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reservation extended successfully',
            'reservation': reservation.to_dict(),
            'additional_cost': additional_cost
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reservations', methods=['GET'])
@token_required
def get_user_reservations():
    """Get user's reservations"""
    try:
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        
        reservations = Reservation.query.filter_by(
            user_id=request.current_user_id
        ).order_by(Reservation.created_at.desc()).all()
        
        # Enhance reservation data with lot information
        enhanced_reservations = []
        for reservation in reservations:
            try:
                res_data = reservation.to_dict()
                
                # Add parking lot and spot information
                spot = ParkingSpot.query.get(reservation.spot_id)
                if spot:
                    lot = ParkingLot.query.get(spot.lot_id)
                    res_data['parking_spot'] = {
                        'id': spot.id,
                        'spot_number': spot.spot_number,
                        'status': spot.status
                    }
                    res_data['parking_lot'] = {
                        'id': lot.id,
                        'prime_location_name': lot.prime_location_name,
                        'address': lot.address,
                        'price': float(lot.price)
                    } if lot else None
                    
                    # Add arrival_timestamp for frontend compatibility
                    res_data['arrival_timestamp'] = res_data['parking_timestamp']
                    
                    # Safely calculate parking duration
                    try:
                        res_data['parking_duration'] = reservation.calculate_parking_duration()
                    except Exception:
                        res_data['parking_duration'] = 0
                
                enhanced_reservations.append(res_data)
                
            except Exception as e:
                # If there's an error with a specific reservation, skip it but log the error
                print(f"Error processing reservation {reservation.id}: {str(e)}")
                continue
        
        return jsonify(enhanced_reservations), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/debug/spot-status', methods=['GET'])
@token_required
def debug_spot_status():
    """Debug endpoint to check parking spot status consistency"""
    try:
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        
        # Get all spots and their current reservations
        spots_info = []
        spots = ParkingSpot.query.all()
        
        for spot in spots:
            # Get active/reserved reservations for this spot
            active_reservations = Reservation.query.filter_by(
                spot_id=spot.id
            ).filter(
                Reservation.status.in_(['reserved', 'active'])
            ).all()
            
            lot = ParkingLot.query.get(spot.lot_id)
            
            spots_info.append({
                'spot_id': spot.id,
                'spot_number': spot.spot_number,
                'lot_name': lot.prime_location_name if lot else 'Unknown',
                'spot_status': spot.status,
                'active_reservations_count': len(active_reservations),
                'active_reservations': [
                    {
                        'id': r.id,
                        'user_id': r.user_id,
                        'status': r.status,
                        'vehicle_number': r.vehicle_number,
                        'created_at': r.created_at.isoformat() if r.created_at else None
                    } for r in active_reservations
                ]
            })
        
        # Find inconsistencies
        inconsistent_spots = [
            s for s in spots_info 
            if (s['spot_status'] == 'A' and s['active_reservations_count'] > 0) or
               (s['spot_status'] in ['R', 'O'] and s['active_reservations_count'] == 0)
        ]
        
        return jsonify({
            'total_spots': len(spots_info),
            'inconsistent_spots_count': len(inconsistent_spots),
            'inconsistent_spots': inconsistent_spots,
            'all_spots': spots_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
