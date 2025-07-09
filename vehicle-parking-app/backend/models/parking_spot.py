from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from . import Base

class ParkingSpot(Base):
    __tablename__ = 'parking_spots'

    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey('parking_lots.id'), nullable=False)
    status = Column(String(1), nullable=False)  # O for occupied, A for available

    parking_lot = relationship("ParkingLot", back_populates="spots")

    def __init__(self, lot_id, status='A'):
        self.lot_id = lot_id
        self.status = status

    def __repr__(self):
        return f"<ParkingSpot(id={self.id}, lot_id={self.lot_id}, status='{self.status}')>"