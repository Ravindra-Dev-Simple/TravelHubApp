from fastapi import APIRouter, Depends, HTTPException
from app.db.session import SessionLocal
from app.db.dependencies import get_db
from app.models.invoiceModel import Invoice
from app.models.booking import Booking
from app.core.security import Session
from app.core.security import get_current_user
from app.services.invoice_service import generate_invoice_pdf
import uuid

router = APIRouter(prefix="/invoice", tags=["Invoice"])


@router.get("/bookings/{booking_id}/invoice")
async def generate_invoice(booking_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)
):

    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    user = current_user
    data = {"booking_details": {
        "id": booking.id,
        "check_in": booking.check_in,
        "check_out": booking.check_out,
        "total_price": float(booking.total_price),
        "status": booking.status,
        "expires_at": booking.expires_at,
        "user": {
            "id": booking.user.id,
            "email": booking.user.email
        },
        "hotel": {
            "id": booking.hotel.id,
            "name": booking.hotel.name,
            "description": booking.hotel.description,
            "city": booking.hotel.city,
            "address": booking.hotel.address,
            "amenities": booking.hotel.amenities
        },
        "room": {
            "id": booking.room.id,
            "room_type": booking.room.room_type,
            "max_guests": booking.room.max_guests,
            "base_price": float(booking.room.base_price)
        }
    }}


    invoice_number, file_path = generate_invoice_pdf(data)

    return {
        "invoice_number": invoice_number,
        "download_path": file_path
    }
