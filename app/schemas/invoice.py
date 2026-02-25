from pydantic import BaseModel
from datetime import datetime

class InvoiceResponse(BaseModel):
    invoice_number: str
    booking_id: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    currency: str
    status: str
    pdf_url: str | None

    class Config:
        from_attributes = True
