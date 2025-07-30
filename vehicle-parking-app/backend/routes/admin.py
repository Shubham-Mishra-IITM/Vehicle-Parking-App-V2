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
        total_spots = ParkingSpot.query.count()
        
        # Get spot statistics
        available_spots = ParkingSpot.query.filter_by(status='A').count()
        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
        reserved_spots = ParkingSpot.query.filter_by(status='R').count()
        
        # Get reservation statistics
        total_reservations = Reservation.query.count()
        active_reservations = Reservation.query.filter_by(status='active').count()
        completed_reservations = Reservation.query.filter_by(status='completed').count()
        
        # Calculate total revenue from completed reservations
        from sqlalchemy import func
        total_revenue_result = db.session.query(
            func.sum(Reservation.parking_cost)
        ).filter(
            Reservation.status == 'completed',
            Reservation.parking_cost.isnot(None)
        ).scalar()
        
        total_revenue = float(total_revenue_result) if total_revenue_result else 0.0
        
        dashboard_data = {
            'statistics': {
                'total_users': total_users,
                'total_parking_lots': total_parking_lots,
                'total_spots': total_spots,
                'available_spots': available_spots,
                'occupied_spots': occupied_spots,
                'reserved_spots': reserved_spots,
                'total_reservations': total_reservations,
                'active_reservations': active_reservations,
                'completed_reservations': completed_reservations,
                'total_revenue': total_revenue
            }
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots', methods=['GET'])
@admin_required
def get_parking_lots():
    """Get all parking lots"""
    try:
        from models.parking_lot import ParkingLot
        
        lots = ParkingLot.query.filter_by(is_active=True).all()
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
        required_fields = ['location', 'total_spots', 'price_per_hour']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate data types
        try:
            total_spots = int(data['total_spots'])
            price_per_hour = float(data['price_per_hour'])
        except ValueError:
            return jsonify({'error': 'Invalid data format'}), 400
        
        if total_spots <= 0:
            return jsonify({'error': 'Total spots must be positive'}), 400
        if price_per_hour <= 0:
            return jsonify({'error': 'Price per hour must be positive'}), 400
        
        # Create the parking lot
        new_lot = ParkingLot(
            location=data['location'],
            total_spots=total_spots,
            price_per_hour=price_per_hour,
            is_active=True
        )
        
        db.session.add(new_lot)
        db.session.flush()  # To get the ID
        
        # Create parking spots for this lot
        for i in range(1, total_spots + 1):
            spot = ParkingSpot(
                lot_id=new_lot.id,
                spot_number=f'P{i:03d}',  # P001, P002, etc.
                status='A'  # Available
            )
            db.session.add(spot)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Parking lot created successfully',
            'parking_lot': new_lot.to_dict()
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
        
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'location' in data:
            lot.location = data['location']
        
        if 'price_per_hour' in data:
            try:
                price_per_hour = float(data['price_per_hour'])
                if price_per_hour <= 0:
                    return jsonify({'error': 'Price per hour must be positive'}), 400
                lot.price_per_hour = price_per_hour
            except ValueError:
                return jsonify({'error': 'Invalid price format'}), 400
        
        if 'total_spots' in data:
            try:
                new_total_spots = int(data['total_spots'])
                if new_total_spots <= 0:
                    return jsonify({'error': 'Total spots must be positive'}), 400
                
                current_spots = ParkingSpot.query.filter_by(lot_id=lot_id).count()
                
                if new_total_spots > current_spots:
                    # Add new spots
                    for i in range(current_spots + 1, new_total_spots + 1):
                        spot = ParkingSpot(
                            lot_id=lot_id,
                            spot_number=f'P{i:03d}',
                            status='A'
                        )
                        db.session.add(spot)
                elif new_total_spots < current_spots:
                    # Check if any spots to be removed are occupied
                    spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot_id).offset(new_total_spots).all()
                    occupied_spots = [spot for spot in spots_to_remove if spot.status in ['R', 'O']]
                    
                    if occupied_spots:
                        return jsonify({'error': 'Cannot reduce spots: some spots are reserved or occupied'}), 400
                    
                    # Remove excess spots
                    for spot in spots_to_remove:
                        db.session.delete(spot)
                
                lot.total_spots = new_total_spots
                
            except ValueError:
                return jsonify({'error': 'Invalid total spots format'}), 400
        
        if 'is_active' in data:
            lot.is_active = bool(data['is_active'])
        
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
    """Delete a parking lot"""
    try:
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        from models.reservation import Reservation
        from database import db
        
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        # Check for active reservations
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        spot_ids = [spot.id for spot in spots]
        
        active_reservations = Reservation.query.filter(
            Reservation.spot_id.in_(spot_ids),
            Reservation.status.in_(['pending', 'active'])
        ).count()
        
        if active_reservations > 0:
            return jsonify({'error': 'Cannot delete parking lot with active reservations'}), 400
        
        # Soft delete by setting is_active to False
        lot.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/parking-lots/<int:lot_id>/spots', methods=['GET'])
@admin_required
def get_parking_spots(lot_id):
    """Get all parking spots for a specific lot"""
    try:
        from models.parking_spot import ParkingSpot
        
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        return jsonify([spot.to_dict() for spot in spots]), 200
        
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

@admin_bp.route('/reservations/<int:reservation_id>/complete', methods=['PUT'])
@admin_required
def complete_reservation(reservation_id):
    """Complete a reservation manually"""
    try:
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from datetime import datetime
        from database import db
        
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        if reservation.status != 'active':
            return jsonify({'error': 'Can only complete active reservations'}), 400
        
        # Calculate parking cost if not already set
        if not reservation.parking_cost and reservation.parked_at:
            from models.parking_lot import ParkingLot
            
            spot = ParkingSpot.query.get(reservation.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            
            # Calculate hours parked
            now = datetime.utcnow()
            time_diff = now - reservation.parked_at
            hours_parked = max(1, int(time_diff.total_seconds() / 3600))  # Minimum 1 hour
            
            reservation.parking_cost = hours_parked * lot.price_per_hour
        
        # Update reservation status
        reservation.status = 'completed'
        reservation.completed_at = datetime.utcnow()
        
        # Update spot status
        spot = ParkingSpot.query.get(reservation.spot_id)
        if spot:
            spot.status = 'A'  # Available
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reservation completed successfully',
            'reservation': reservation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@admin_required
def cancel_reservation(reservation_id):
    """Cancel a reservation"""
    try:
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from database import db
        
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        if reservation.status == 'completed':
            return jsonify({'error': 'Cannot cancel completed reservation'}), 400
        
        # Update spot status to available
        spot = ParkingSpot.query.get(reservation.spot_id)
        if spot:
            spot.status = 'A'  # Available
        
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

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all non-admin users"""
    try:
        from models.user import User
        
        # Only return users with role 'user', not 'admin'
        users = User.query.filter_by(role='user').all()
        users_data = []
        
        for user in users:
            user_dict = user.to_dict()
            users_data.append(user_dict)
        
        return jsonify(users_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/statistics', methods=['GET'])
@admin_required
def get_user_statistics(user_id):
    """Get statistics for a specific user"""
    try:
        from models.user import User
        from models.reservation import Reservation
        from sqlalchemy import func
        from database import db
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user statistics
        total_reservations = Reservation.query.filter_by(user_id=user_id).count()
        active_reservations = Reservation.query.filter_by(user_id=user_id, status='active').count()
        
        # Get total spent (sum of parking costs for completed reservations)
        total_spent_result = db.session.query(
            func.sum(Reservation.parking_cost)
        ).filter(
            Reservation.user_id == user_id,
            Reservation.status == 'completed',
            Reservation.parking_cost.isnot(None)
        ).scalar()
        
        total_spent = float(total_spent_result) if total_spent_result else 0.0
        
        statistics = {
            'user': user.to_dict(),
            'total_reservations': total_reservations,
            'active_reservations': active_reservations,
            'total_spent': total_spent
        }
        
        return jsonify(statistics), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    """Update user role"""
    try:
        from models.user import User
        from database import db
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['user', 'admin']:
            return jsonify({'error': 'Invalid role. Must be user or admin'}), 400
        
        # Prevent admin from changing their own role
        if user_id == request.current_user_id:
            return jsonify({'error': 'You cannot change your own role'}), 400
        
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': f'User role updated to {new_role} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/test-reminders', methods=['POST'])
@admin_required
def test_daily_reminders():
    """Manually trigger daily reminders for testing"""
    try:
        # Import the task function directly and execute it synchronously
        from tasks.daily_reminders import send_daily_reminders_sync
        from app import app
        
        # Execute the task directly within Flask app context (synchronous)
        with app.app_context():
            # Call the task function directly (not via Celery)
            result = send_daily_reminders_sync()
            
            return jsonify({
                'message': 'Daily reminders executed successfully (synchronous)',
                'result': result,
                'status': 'completed'
            }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': f'Failed to execute reminders: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@admin_bp.route('/test-reminders-async', methods=['POST'])
@admin_required
def test_daily_reminders_async():
    """Manually trigger daily reminders via Celery (async)"""
    try:
        # Import the Celery task directly
        from tasks.daily_reminders import send_daily_reminders
        
        # Trigger the task asynchronously
        task = send_daily_reminders.delay()
        
        return jsonify({
            'message': 'Daily reminders task triggered successfully via Celery',
            'task_id': task.id,
            'status': 'started'
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': f'Failed to trigger reminders: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@admin_bp.route('/test-new-lot-notifications', methods=['POST'])
@admin_required
def test_new_lot_notifications():
    """Manually trigger new parking lot notifications for testing"""
    try:
        from tasks.daily_reminders import send_new_parking_lot_notifications
        
        # Trigger the task asynchronously
        task = send_new_parking_lot_notifications.delay()
        
        return jsonify({
            'message': 'New parking lot notifications task triggered successfully',
            'task_id': task.id,
            'status': 'started'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to trigger notifications: {str(e)}'}), 500

@admin_bp.route('/test-admin-summary', methods=['POST'])
@admin_required
def test_admin_summary():
    """Manually trigger admin daily summary for testing"""
    try:
        from tasks.daily_reminders import send_admin_daily_summary
        
        # Trigger the task asynchronously
        task = send_admin_daily_summary.delay()
        
        return jsonify({
            'message': 'Admin daily summary task triggered successfully',
            'task_id': task.id,
            'status': 'started'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to trigger admin summary: {str(e)}'}), 500

@admin_bp.route('/task-status/<task_id>', methods=['GET'])
@admin_required
def get_task_status(task_id):
    """Get the status of a Celery task"""
    try:
        from tasks.celery_app import celery
        
        task = celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Task is waiting to be processed'
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
                'result': task.result
            }
        else:  # FAILURE
            response = {
                'state': task.state,
                'error': str(task.info)
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get task status: {str(e)}'}), 500

@admin_bp.route('/test-monthly-reports', methods=['POST'])
@admin_required
def test_monthly_reports():
    """Test monthly reports functionality"""
    try:
        from tasks.monthly_reports import send_monthly_reports_task
        from datetime import datetime
        
        # Get current month/year or from request
        month = request.json.get('month', datetime.now().month) if request.json else datetime.now().month
        year = request.json.get('year', datetime.now().year) if request.json else datetime.now().year
        user_id = request.json.get('user_id') if request.json else None  # Optional - test specific user
        
        result = {
            'success': True,
            'message': f'Monthly reports test initiated for {month}/{year}',
            'reports_sent': 0,
            'errors': []
        }
        
        # Test synchronously for immediate results
        if user_id:
            # Test for specific user
            from models.user import User
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            try:
                from tasks.monthly_reports import generate_monthly_report_data, generate_monthly_report_html, send_email
                
                # Generate report data
                report_data = generate_monthly_report_data(user.id, month, year)
                
                # Generate HTML
                html_content = generate_monthly_report_html(user, report_data, month, year)
                
                # Send email
                subject = f"Monthly Parking Report - {month}/{year}"
                send_email(user.email, subject, html_content)
                
                result['reports_sent'] = 1
                result['message'] = f'Monthly report sent to {user.username} ({user.email})'
                result['report_data'] = {
                    'total_reservations': report_data['total_reservations'],
                    'completed_reservations': report_data['completed_reservations'],
                    'total_amount_spent': report_data['total_amount_spent'],
                    'total_hours_parked': report_data['total_hours_parked']
                }
                
            except Exception as e:
                result['errors'].append(f'Error sending report to {user.username}: {str(e)}')
                result['success'] = False
        else:
            # Test for all users (limit to first 5 for testing)
            from models.user import User
            users = User.query.limit(5).all()
            
            for user in users:
                try:
                    from tasks.monthly_reports import generate_monthly_report_data, generate_monthly_report_html, send_email
                    
                    # Generate report data
                    report_data = generate_monthly_report_data(user.id, month, year)
                    
                    # Only send if user has any activity
                    if report_data['total_reservations'] > 0:
                        # Generate HTML
                        html_content = generate_monthly_report_html(user, report_data, month, year)
                        
                        # Send email
                        subject = f"Monthly Parking Report - {month}/{year}"
                        send_email(user.email, subject, html_content)
                        
                        result['reports_sent'] += 1
                    
                except Exception as e:
                    result['errors'].append(f'Error sending report to {user.username}: {str(e)}')
            
            result['message'] = f'Monthly reports test completed. Sent {result["reports_sent"]} reports.'
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/test-monthly-reports-async', methods=['POST'])
@admin_required
def test_monthly_reports_async():
    """Test monthly reports functionality asynchronously"""
    try:
        from tasks.monthly_reports import send_monthly_reports_task
        from datetime import datetime
        
        # Get current month/year or from request
        month = request.json.get('month', datetime.now().month) if request.json else datetime.now().month
        year = request.json.get('year', datetime.now().year) if request.json else datetime.now().year
        
        # Queue the task
        task = send_monthly_reports_task.delay(month, year)
        
        return jsonify({
            'success': True,
            'message': f'Monthly reports task queued for {month}/{year}',
            'task_id': task.id,
            'status': 'PENDING'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/preview-monthly-report/<int:user_id>', methods=['GET'])
@admin_required
def preview_monthly_report(user_id):
    """Preview monthly report HTML for a specific user"""
    try:
        from models.user import User
        from tasks.monthly_reports import generate_monthly_report_data, generate_monthly_report_html
        from datetime import datetime
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get month/year from query params or use current
        month = int(request.args.get('month', datetime.now().month))
        year = int(request.args.get('year', datetime.now().year))
        
        # Generate report data
        report_data = generate_monthly_report_data(user.id, month, year)
        
        # Generate HTML
        html_content = generate_monthly_report_html(user, report_data, month, year)
        
        # Return HTML for preview
        return html_content, 200, {'Content-Type': 'text/html'}
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
