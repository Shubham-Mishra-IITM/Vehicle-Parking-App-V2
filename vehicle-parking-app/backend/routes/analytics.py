from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date
import logging

analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)

@analytics_bp.route('/admin/analytics', methods=['GET'])
@jwt_required()
def get_analytics_data():
    """Get comprehensive analytics data for admin dashboard"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get the user from database to check role
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get current parking status (simplified)
        parking_status = {
            'available': ParkingSpot.query.filter_by(status='A').count(),
            'occupied': ParkingSpot.query.filter_by(status='O').count(),
            'reserved': ParkingSpot.query.filter_by(status='R').count()
        }
        
        # Generate simple mock data for testing
        daily_revenue = {
            'dates': ['07/01', '07/02', '07/03', '07/04', '07/05', '07/06', '07/07'],
            'amounts': [120.50, 89.25, 156.75, 203.40, 95.60, 178.90, 145.30]
        }
        
        # Get parking lot utilization (simplified with mock data for now)
        lot_utilization = {
            'lot_names': ['Downtown', 'Mall', 'Airport', 'Stadium'],
            'utilization_rates': [85, 67, 92, 45]
        }
        
        # Simple mock data for other charts
        weekly_revenue = {
            'weeks': ['Week 28', 'Week 29', 'Week 30', 'Week 31'],
            'amounts': [850.75, 920.40, 1120.85, 995.60]
        }
        
        peak_hours = {
            'hours': ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00'],
            'occupancy': [5, 12, 25, 35, 28, 22, 30, 28, 25, 20, 24, 32, 28, 15, 8, 3]
        }
        
        # Get basic statistics
        total_completed = Reservation.query.filter_by(status='completed').count()
        total_revenue_result = db.session.query(func.sum(Reservation.parking_cost)).filter_by(status='completed').scalar()
        total_revenue = float(total_revenue_result) if total_revenue_result else 0
        
        analytics_data = {
            'parking_status': parking_status,
            'daily_revenue': daily_revenue,
            'lot_utilization': lot_utilization,
            'weekly_revenue': weekly_revenue,
            'peak_hours': peak_hours,
            'summary_stats': {
                'total_completed_reservations': total_completed,
                'total_revenue': total_revenue,
                'average_parking_duration': 2.5
            }
        }
        
        return jsonify(analytics_data)
        
    except Exception as e:
        logger.error(f"Error fetching analytics data: {str(e)}")
        logger.error(f"Exception details: {e.__class__.__name__}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to fetch analytics data: {str(e)}'}), 500

@analytics_bp.route('/public/stats', methods=['GET'])
def get_public_stats():
    """Get public statistics for home page (no authentication required)"""
    try:
        # Get basic public statistics
        total_parking_lots = ParkingLot.query.count()
        total_parking_spots = ParkingSpot.query.count()
        available_spots = ParkingSpot.query.filter_by(status='A').count()
        total_reservations = Reservation.query.count()
        
        # Calculate utilization rate
        utilization_rate = 0
        if total_parking_spots > 0:
            occupied_spots = total_parking_spots - available_spots
            utilization_rate = round((occupied_spots / total_parking_spots) * 100, 1)
        
        public_stats = {
            'total_parking_lots': total_parking_lots,
            'total_parking_spots': total_parking_spots,
            'available_spots': available_spots,
            'utilization_rate': utilization_rate,
            'total_reservations': total_reservations
        }
        
        return jsonify(public_stats)
        
    except Exception as e:
        logger.error(f"Error fetching public stats: {str(e)}")
        return jsonify({
            'total_parking_lots': 0,
            'total_parking_spots': 0,
            'available_spots': 0,
            'utilization_rate': 0,
            'total_reservations': 0
        })
