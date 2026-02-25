from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, DECIMAL, Date, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid
from datetime import datetime


class User(Base):
    __tablename__ = "tbl_users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="customer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    hotels = relationship("Hotel", back_populates="owner")
    bookings = relationship("Booking", back_populates="user")


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


class Room(Base):
    __tablename__ = "tbl_rooms"

    id = Column(String(36), primary_key=True)
    hotel_id = Column(String(36), ForeignKey("tbl_hotels.id"), nullable=False)
    room_type = Column(String(100), nullable=False)
    base_price = Column(DECIMAL(10,2), nullable=False)
    total_rooms = Column(Integer, nullable=False)
    max_guests = Column(Integer, default=2)
    
    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")


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
