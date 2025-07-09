from flask import Blueprint, request, jsonify
from ..models.user import User
from ..models.parking_spot import ParkingSpot
from ..models.reservation import Reservation
from ..utils.auth import token_required
from .. import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/reserve', methods=['POST'])
@token_required
def reserve_parking_spot(current_user):
    data = request.get_json()
    lot_id = data.get('lot_id')

    # Find an available parking spot
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        return jsonify({'message': 'No available parking spots'}), 400

    # Create a reservation
    reservation = Reservation(
        spot_id=spot.id,
        user_id=current_user.id,
        parking_timestamp=datetime.utcnow(),
        parking_cost=spot.price  # Assuming price is stored in ParkingSpot
    )
    spot.status = 'O'  # Mark the spot as occupied
    db.session.add(reservation)
    db.session.commit()

    return jsonify({'message': 'Parking spot reserved', 'reservation_id': reservation.id}), 201

@user_bp.route('/release', methods=['POST'])
@token_required
def release_parking_spot(current_user):
    data = request.get_json()
    reservation_id = data.get('reservation_id')

    reservation = Reservation.query.get(reservation_id)
    if not reservation or reservation.user_id != current_user.id:
        return jsonify({'message': 'Reservation not found or access denied'}), 404

    # Release the parking spot
    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = 'A'  # Mark the spot as available
    db.session.delete(reservation)
    db.session.commit()

    return jsonify({'message': 'Parking spot released'}), 200

@user_bp.route('/my_reservations', methods=['GET'])
@token_required
def my_reservations(current_user):
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'reservation_id': r.id,
        'spot_id': r.spot_id,
        'parking_timestamp': r.parking_timestamp,
        'leaving_timestamp': r.leaving_timestamp,
        'parking_cost': r.parking_cost
    } for r in reservations]), 200