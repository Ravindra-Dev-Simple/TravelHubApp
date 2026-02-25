from sqlalchemy import Column, String, Integer, Text, DateTime
from datetime import datetime
from app.db.base import Base

class Review(Base):
    __tablename__ = "tbl_reviews"

    id = Column(String(36), primary_key=True)

    user_id = Column(String(36), nullable=False)
    hotel_id = Column(String(36), nullable=False)
    booking_id = Column(String(36), nullable=False)

    rating = Column(Integer, nullable=False)
    comment = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
