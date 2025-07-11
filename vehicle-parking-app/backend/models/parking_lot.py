from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# This will be imported from app.py
db = SQLAlchemy()

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'

    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Price per hour
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships (using string names to avoid circular imports)
    parking_spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    
    def get_available_spots_count(self):
        """Return count of available parking spots"""
        from .parking_spot import ParkingSpot
        return ParkingSpot.query.filter_by(
            lot_id=self.id, 
            status='A'
        ).count()
    
    def get_occupied_spots_count(self):
        """Return count of occupied parking spots"""
        from .parking_spot import ParkingSpot
        return ParkingSpot.query.filter_by(
            lot_id=self.id, 
            status='O'
        ).count()
    
    def can_be_deleted(self):
        """Check if parking lot can be deleted (all spots must be available)"""
        return self.get_occupied_spots_count() == 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'prime_location_name': self.prime_location_name,
            'price': float(self.price),
            'address': self.address,
            'pin_code': self.pin_code,
            'number_of_spots': self.number_of_spots,
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_active': self.is_active,
            'available_spots': self.get_available_spots_count(),
            'occupied_spots': self.get_occupied_spots_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<ParkingLot(id={self.id}, location={self.prime_location_name}, price={self.price})>"