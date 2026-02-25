from sqlalchemy import Column, String, DECIMAL, DateTime
from datetime import datetime
from app.db.base import Base

class Invoice(Base):
    __tablename__ = "tbl_invoices"

    id = Column(String(36), primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)

    booking_id = Column(String(36), nullable=False)
    user_id = Column(String(36), nullable=False)

    subtotal = Column(DECIMAL(12,2), nullable=False)
    discount_amount = Column(DECIMAL(12,2), default=0)
    tax_amount = Column(DECIMAL(12,2), default=0)
    total_amount = Column(DECIMAL(12,2), nullable=False)

    currency = Column(String(10), default="INR")

    status = Column(String(20), default="GENERATED")

    pdf_url = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
