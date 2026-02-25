from sqlalchemy import Column, String, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Room(Base):
    __tablename__ = "tbl_rooms"

    id = Column(String(36), primary_key=True)
    hotel_id = Column(String(36), ForeignKey("tbl_hotels.id"),nullable=False)
    room_type = Column(String(100), nullable=False)
    base_price = Column(DECIMAL(10,2), nullable=False)
    total_rooms = Column(Integer, nullable=False)
    max_guests = Column(Integer, default=2)
    
    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")
