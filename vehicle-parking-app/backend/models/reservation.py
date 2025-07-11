from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from decimal import Decimal

# This will be imported from app.py
db = SQLAlchemy()

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Numeric(10, 2), nullable=True)
    total_hours = db.Column(db.Numeric(5, 2), nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, completed, cancelled
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Note: Relationships are defined via backref in other models
    
    def calculate_parking_duration(self):
        """Calculate parking duration in hours"""
        if self.leaving_timestamp:
            duration = self.leaving_timestamp - self.parking_timestamp
            return round(duration.total_seconds() / 3600, 2)  # Convert to hours
        else:
            # If still parked, calculate current duration
            duration = datetime.utcnow() - self.parking_timestamp
            return round(duration.total_seconds() / 3600, 2)
    
    def calculate_cost(self, hourly_rate):
        """Calculate total parking cost based on duration and hourly rate"""
        hours = self.calculate_parking_duration()
        # Minimum charge for 1 hour, then per hour
        billable_hours = max(1, hours)
        return round(Decimal(str(billable_hours)) * Decimal(str(hourly_rate)), 2)
    
    def complete_reservation(self, hourly_rate):
        """Complete the reservation when user leaves"""
        self.leaving_timestamp = datetime.utcnow()
        self.total_hours = self.calculate_parking_duration()
        self.parking_cost = self.calculate_cost(hourly_rate)
        self.status = 'completed'
        self.updated_at = datetime.utcnow()
    
    def cancel_reservation(self, reason=None):
        """Cancel the reservation"""
        self.status = 'cancelled'
        if reason:
            self.remarks = reason
        self.updated_at = datetime.utcnow()
    
    def is_active(self):
        """Check if reservation is currently active"""
        return self.status == 'active' and self.leaving_timestamp is None
    
    def to_dict(self):
        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'vehicle_number': self.vehicle_number,
            'parking_timestamp': self.parking_timestamp.isoformat() if self.parking_timestamp else None,
            'leaving_timestamp': self.leaving_timestamp.isoformat() if self.leaving_timestamp else None,
            'parking_cost': float(self.parking_cost) if self.parking_cost else None,
            'total_hours': float(self.total_hours) if self.total_hours else None,
            'current_duration_hours': self.calculate_parking_duration(),
            'status': self.status,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Reservation(id={self.id}, spot_id={self.spot_id}, user_id={self.user_id}, status={self.status})>"