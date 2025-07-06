from flask import Blueprint, request, jsonify
from backend.models.models import db, ParkingLot, ParkingSpot
from backend.utils.auth import token_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/parking-lot', methods=['POST'])
@token_required(role='admin')
def create_parking_lot(current_user):
    data = request.get_json()

    required_fields = ['name', 'address', 'pin_code', 'price_per_hour', 'number_of_spots']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        lot = ParkingLot(
            name=data['name'],
            address=data['address'],
            pin_code=data['pin_code'],
            price_per_hour=data['price_per_hour'],
            number_of_spots=data['number_of_spots']
        )
        db.session.add(lot)
        db.session.flush()  # Get lot.id before commit

        # Create parking spots
        for _ in range(data['number_of_spots']):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)

        db.session.commit()
        return jsonify({'message': 'Parking lot and spots created successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@admin_bp.route('/parking-lots', methods=['GET'])
@token_required(role='admin')
def list_parking_lots(current_user):
    lots = ParkingLot.query.all()
    result = []

    for lot in lots:
        total_spots = len(lot.spots)
        available = len([spot for spot in lot.spots if spot.status == 'A'])
        occupied = total_spots - available

        result.append({
            "id": lot.id,
            "name": lot.name,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "price_per_hour": lot.price_per_hour,
            "number_of_spots": total_spots,
            "available_spots": available,
            "occupied_spots": occupied
        })

    return jsonify(result), 200


# Update a parking lot (admin only)
@admin_bp.route('/parking-lot/<int:lot_id>', methods=['PUT'])
@token_required(role='admin')
def update_parking_lot(current_user, lot_id):
    data = request.get_json()
    lot = ParkingLot.query.get_or_404(lot_id)

    old_spot_count = lot.number_of_spots
    new_spot_count = data.get('number_of_spots', old_spot_count)

    # Update basic fields
    lot.name = data.get('name', lot.name)
    lot.address = data.get('address', lot.address)
    lot.pin_code = data.get('pin_code', lot.pin_code)
    lot.price_per_hour = data.get('price_per_hour', lot.price_per_hour)

    try:
        if new_spot_count > old_spot_count:
            # Add new spots
            for _ in range(new_spot_count - old_spot_count):
                new_spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(new_spot)

        elif new_spot_count < old_spot_count:
            # Only allow decrease if enough spots are available
            available_spots = [spot for spot in lot.spots if spot.status == 'A']
            diff = old_spot_count - new_spot_count

            if len(available_spots) < diff:
                return jsonify({'error': 'Not enough available spots to reduce count'}), 400

            # Remove extra available spots
            for spot in available_spots[:diff]:
                db.session.delete(spot)

        lot.number_of_spots = new_spot_count
        db.session.commit()

        return jsonify({'message': 'Parking lot updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500