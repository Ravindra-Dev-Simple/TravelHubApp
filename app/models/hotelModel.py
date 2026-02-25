from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Hotel(Base):
    __tablename__ = "tbl_hotels"

    id = Column(String(36), primary_key=True)
    owner_id = Column(String(36), ForeignKey("tbl_users.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    latitude = Column(String(10))
    longitude = Column(String(10))
    city = Column(String(100))
    address = Column(Text)
    amenities = Column(JSON) 
    is_active = Column(Boolean, default=True)
    
    owner = relationship("User", back_populates="hotels")
    rooms = relationship("Room", back_populates="hotel")
    bookings = relationship("Booking", back_populates="hotel")   