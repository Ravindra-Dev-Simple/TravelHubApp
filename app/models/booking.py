from sqlalchemy import Column, String, Date, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Booking(Base):
    __tablename__ = "tbl_bookings"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("tbl_users.id"), nullable=False)
    room_id = Column(String(36), ForeignKey("tbl_rooms.id"), nullable=False)
    hotel_id = Column(String(36), ForeignKey("tbl_hotels.id"), nullable=False)

    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)

    total_price = Column(DECIMAL(12,2), nullable=False)
    status = Column(String(20), default="RESERVED")
    expires_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
