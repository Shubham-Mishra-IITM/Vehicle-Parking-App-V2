# Import models - db instance will be injected from app.py
from .user import User
from .parking_lot import ParkingLot
from .parking_spot import ParkingSpot
from .reservation import Reservation

__all__ = ['User', 'ParkingLot', 'ParkingSpot', 'Reservation']