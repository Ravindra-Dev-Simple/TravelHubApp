from sqlalchemy import Column, String, Integer, Date, DECIMAL
from app.db.base import Base

class Inventory(Base):
    __tablename__ = "tbl_inventory"

    id = Column(String(36), primary_key=True)
    room_id = Column(String(36), nullable=False)
    date = Column(Date, nullable=False)
    available_count = Column(Integer, nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)
