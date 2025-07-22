# Import models and shared database instance
from database import db
from .user import User
from .parking_lot import ParkingLot
from .parking_spot import ParkingSpot
from .reservation import Reservation

__all__ = ['db', 'User', 'ParkingLot', 'ParkingSpot', 'Reservation']