from flask import Blueprint, request, jsonify
from ..models.parking_lot import ParkingLot
from ..models.parking_spot import ParkingSpot
from .. import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/parking-lots', methods=['POST'])
def create_parking_lot():
    data = request.json
    new_lot = ParkingLot(
        prime_location_name=data['prime_location_name'],
        price=data['price'],
        address=data['address'],
        pin_code=data['pin_code'],
        number_of_spots=data['number_of_spots']
    )
    db.session.add(new_lot)
    db.session.commit()
    
    for _ in range(data['number_of_spots']):
        new_spot = ParkingSpot(lot_id=new_lot.id, status='A')
        db.session.add(new_spot)
    
    db.session.commit()
    return jsonify({'message': 'Parking lot created successfully'}), 201

@admin_bp.route('/admin/parking-lots/<int:lot_id>', methods=['PUT'])
def edit_parking_lot(lot_id):
    data = request.json
    lot = ParkingLot.query.get_or_404(lot_id)
    
    lot.prime_location_name = data.get('prime_location_name', lot.prime_location_name)
    lot.price = data.get('price', lot.price)
    lot.address = data.get('address', lot.address)
    lot.pin_code = data.get('pin_code', lot.pin_code)
    lot.number_of_spots = data.get('number_of_spots', lot.number_of_spots)
    
    db.session.commit()
    return jsonify({'message': 'Parking lot updated successfully'}), 200

@admin_bp.route('/admin/parking-lots/<int:lot_id>', methods=['DELETE'])
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count() > 0:
        return jsonify({'message': 'Cannot delete parking lot with occupied spots'}), 400
    
    db.session.delete(lot)
    db.session.commit()
    return jsonify({'message': 'Parking lot deleted successfully'}), 200

@admin_bp.route('/admin/parking-lots', methods=['GET'])
def get_parking_lots():
    lots = ParkingLot.query.all()
    return jsonify([lot.to_dict() for lot in lots]), 200

@admin_bp.route('/admin/users', methods=['GET'])
def get_users():
    users = User.query.all()  # Assuming User model is imported
    return jsonify([user.to_dict() for user in users]), 200