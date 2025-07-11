from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# This will be imported from app.py
db = SQLAlchemy()

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(10), nullable=False)  # e.g., "A1", "B2", etc.
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)  # A=Available, O=Occupied
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships (using string names to avoid circular imports)
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True, cascade='all, delete-orphan')
    
    def is_available(self):
        """Check if the parking spot is available"""
        return self.status == 'A' and self.is_active
    
    def is_occupied(self):
        """Check if the parking spot is occupied"""
        return self.status == 'O'
    
    def occupy_spot(self):
        """Mark the spot as occupied"""
        self.status = 'O'
        self.updated_at = datetime.utcnow()
    
    def release_spot(self):
        """Mark the spot as available"""
        self.status = 'A'
        self.updated_at = datetime.utcnow()
    
    def get_current_reservation(self):
        """Get the current active reservation for this spot"""
        from .reservation import Reservation
        return Reservation.query.filter_by(
            spot_id=self.id,
            leaving_timestamp=None
        ).first()
    
    def to_dict(self):
        current_reservation = self.get_current_reservation()
        return {
            'id': self.id,
            'spot_number': self.spot_number,
            'lot_id': self.lot_id,
            'status': self.status,
            'is_active': self.is_active,
            'current_reservation': current_reservation.to_dict() if current_reservation else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<ParkingSpot(id={self.id}, spot_number={self.spot_number}, lot_id={self.lot_id}, status='{self.status}')>"