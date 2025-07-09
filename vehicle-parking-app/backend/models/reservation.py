from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from . import Base

class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True)
    spot_id = Column(Integer, ForeignKey('parking_spots.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    parking_timestamp = Column(DateTime, default=datetime.utcnow)
    leaving_timestamp = Column(DateTime, nullable=True)
    parking_cost = Column(Numeric(10, 2), nullable=False)

    spot = relationship("ParkingSpot", back_populates="reservations")
    user = relationship("User", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation(id={self.id}, spot_id={self.spot_id}, user_id={self.user_id}, parking_timestamp={self.parking_timestamp}, leaving_timestamp={self.leaving_timestamp}, parking_cost={self.parking_cost})>"