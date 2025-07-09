from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class ParkingLot(Base):
    __tablename__ = 'parking_lots'

    id = Column(Integer, primary_key=True)
    prime_location_name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    pin_code = Column(String, nullable=False)
    number_of_spots = Column(Integer, nullable=False)

    parking_spots = relationship("ParkingSpot", back_populates="parking_lot")

    def __repr__(self):
        return f"<ParkingLot(id={self.id}, location={self.prime_location_name}, price={self.price})>"