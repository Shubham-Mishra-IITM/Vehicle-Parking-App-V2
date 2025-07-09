from flask import Blueprint, request, jsonify
from ..models.parking_lot import ParkingLot
from ..models.parking_spot import ParkingSpot
from ..utils.cache import cache

parking_bp = Blueprint('parking', __name__)

@parking_bp.route('/parking-lots', methods=['GET'])
@cache.cached(timeout=60)
def get_parking_lots():
    parking_lots = ParkingLot.query.all()
    return jsonify([lot.to_dict() for lot in parking_lots]), 200

@parking_bp.route('/parking-lots', methods=['POST'])
def create_parking_lot():
    data = request.json
    new_lot = ParkingLot(
        prime_location_name=data['prime_location_name'],
        price=data['price'],
        address=data['address'],
        pin_code=data['pin_code'],
        number_of_spots=data['number_of_spots']
    )
    new_lot.save()
    return jsonify(new_lot.to_dict()), 201

@parking_bp.route('/parking-lots/<int:lot_id>', methods=['PUT'])
def update_parking_lot(lot_id):
    data = request.json
    lot = ParkingLot.query.get_or_404(lot_id)
    lot.prime_location_name = data.get('prime_location_name', lot.prime_location_name)
    lot.price = data.get('price', lot.price)
    lot.address = data.get('address', lot.address)
    lot.pin_code = data.get('pin_code', lot.pin_code)
    lot.number_of_spots = data.get('number_of_spots', lot.number_of_spots)
    lot.save()
    return jsonify(lot.to_dict()), 200

@parking_bp.route('/parking-lots/<int:lot_id>', methods=['DELETE'])
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if lot.has_occupied_spots():
        return jsonify({"error": "Cannot delete a parking lot with occupied spots."}), 400
    lot.delete()
    return jsonify({"message": "Parking lot deleted successfully."}), 204

@parking_bp.route('/parking-spots/<int:lot_id>', methods=['GET'])
def get_parking_spots(lot_id):
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return jsonify([spot.to_dict() for spot in spots]), 200

@parking_bp.route('/parking-spots/<int:spot_id>/occupy', methods=['POST'])
def occupy_parking_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    if spot.status == 'O':
        return jsonify({"error": "Parking spot is already occupied."}), 400
    spot.status = 'O'
    spot.save()
    return jsonify(spot.to_dict()), 200

@parking_bp.route('/parking-spots/<int:spot_id>/release', methods=['POST'])
def release_parking_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    if spot.status == 'A':
        return jsonify({"error": "Parking spot is already available."}), 400
    spot.status = 'A'
    spot.save()
    return jsonify(spot.to_dict()), 200