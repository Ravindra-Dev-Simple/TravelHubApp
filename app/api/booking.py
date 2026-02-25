from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.booking import BookingCreate, AvailabilityRequest, AvailableRoomResponse
from app.models.booking import Booking
from app.models.roomModel import Room
from app.db.dependencies import get_db
from app.core.security import get_current_user
import uuid
from datetime import datetime, timedelta
from app.models.hotelModel import Hotel
from app.models.usersModel import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/search-availability")
def search_availability(
    data: AvailabilityRequest,
    db: Session = Depends(get_db)
):
    hotel = db.query(Hotel).filter(Hotel.id == data.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel Not Found")
    
    if data.check_in >= data.check_out:
        raise HTTPException(status_code=400, detail="Invalid date range")

    rooms = db.query(Room).filter(
        Room.hotel_id == data.hotel_id
    ).all()

    available_rooms = []

    for room in rooms:

        inventories = db.execute(
            text("""
                SELECT * FROM tbl_inventory
                WHERE room_id = :room_id
                AND date >= :check_in
                AND date < :check_out
            """),
            {
                "room_id": room.id,
                "check_in": data.check_in,
                "check_out": data.check_out
            }
        ).fetchall()

        if not inventories:
            continue

        # ✅ Check if available for all days
        is_available = all(inv.available_count > 0 for inv in inventories)

        if not is_available:
            continue

        total_price = sum(float(inv.price) for inv in inventories)

        available_rooms.append({
            "room_id": room.id,
            "room_type": room.room_type,
            "max_guests": room.max_guests,
            "total_price": total_price
        })

    return available_rooms


@router.post("/BookHotelRoom")
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if data.check_in >= data.check_out:
        raise HTTPException(status_code=400, detail="Invalid date range")

    try:
        # 🔒 LOCK inventory rows
        inventories = db.execute(
            text("""
                SELECT * FROM tbl_inventory
                WHERE room_id = :room_id
                AND date >= :check_in
                AND date < :check_out
                FOR UPDATE
            """),
            {
                "room_id": data.room_id,
                "check_in": data.check_in,
                "check_out": data.check_out
            }
        ).fetchall()

        if not inventories:
            raise HTTPException(status_code=404, detail="No inventory found")

        total_price = 0

        for inv in inventories:
            if inv.available_count <= 0:
                raise HTTPException(status_code=400, detail="Room not available")
            total_price += float(inv.price)

        # 🔻 Deduct availability
        db.execute(
            text("""
                UPDATE tbl_inventory
                SET available_count = available_count - 1
                WHERE room_id = :room_id
                AND date >= :check_in
                AND date < :check_out
            """),
            {
                "room_id": data.room_id,
                "check_in": data.check_in,
                "check_out": data.check_out
            }
        )
        # 🔍 Prevent overlapping booking for same user & same room

        overlap = db.query(Booking).filter(
            Booking.user_id == current_user.id,
            Booking.hotel_id == data.hotel_id,
            Booking.status.in_(["RESERVED", "CONFIRMED"]),
            Booking.check_in < data.check_out,
            Booking.check_out > data.check_in
        ).first()

        if overlap:
            raise HTTPException(
                status_code=400,
                detail="You already have a booking for this room in selected dates"
            )
        
        # 📝 Create booking record
        booking = Booking(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            hotel_id = data.hotel_id,
            room_id=data.room_id,
            check_in=data.check_in,
            check_out=data.check_out,
            total_price=total_price,
            status="RESERVED",
            expires_at=datetime.utcnow() + timedelta(minutes=1)
        )

        db.add(booking)
        db.commit()

        return {
            "message": "Booking successful",
            "booking_id": booking.id,
            "total_price": total_price
        }

    except Exception as e:
        db.rollback()
        raise e


@router.post("/HotelRoomCancel/{booking_id}")
def cancel_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status not in ["RESERVED", "CONFIRMED"]:
        raise HTTPException(status_code=400, detail="Cannot cancel this booking")

    try:
        db.execute(
            text("""
                SELECT * FROM tbl_inventory
                WHERE room_id = :room_id
                AND date >= :check_in
                AND date < :check_out
                FOR UPDATE
            """),
            {
                "room_id": booking.room_id,
                "check_in": booking.check_in,
                "check_out": booking.check_out
            }
        )


        db.execute(
            text("""
                UPDATE tbl_inventory
                SET available_count = available_count + 1
                WHERE room_id = :room_id
                AND date >= :check_in
                AND date < :check_out
            """),
            {
                "room_id": booking.room_id,
                "check_in": booking.check_in,
                "check_out": booking.check_out
            }
        )

        booking.status = "CANCELLED"

        db.commit()

        return {"message": "Processing to payment"}

    except:
        db.rollback()
        raise


# @router.get("/bookings/{booking_id}")
# async def get_booking_details(
#     booking_id: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     booking = db.query(Booking).filter(
#         Booking.id == booking_id,
#         Booking.user_id == current_user.id
#     ).first()

#     if not booking:
#         raise HTTPException(status_code=404, detail="Booking not found")

#     return booking

@router.get("/bookings_list")
async def get_user_bookings_lists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).all()

    if not bookings:
        return {
            "status": "Success",
            "message": "No bookings found",
            "data": {"booking_details": []}
        }

    booking_details = []

    for booking in bookings:

        hotel = db.query(Hotel).filter(
            Hotel.id == booking.hotel_id
        ).first()       

        room = db.query(Room).filter(
            Room.id == booking.room_id
        ).first()

        booking_details.append({
            "id": booking.id,
            "check_in": booking.check_in,
            "check_out": booking.check_out,
            "total_price": float(booking.total_price),
            "status": booking.status,
            "expires_at": booking.expires_at,
            "user": {
                "id": current_user.id,
                "email": current_user.email
            },
            "hotel": {
                "id": hotel.id if hotel else None,
                "name": hotel.name if hotel else None,
                "description": hotel.description if hotel else None,
                "city": hotel.city if hotel else None,
                "address": hotel.address if hotel else None,
                "amenities": hotel.amenities if hotel else None
            },
            "room": {
                "id": room.id if room else None,
                "room_type": room.room_type if room else None,
                "max_guests": room.max_guests if room else None,
                "base_price": float(room.base_price) if room else None
            }
        })

    return {
        "status": "Success",
        "message": "Booking details successfully fetched",
        "data": {"booking_details": booking_details}
    }


@router.get("/bookings_details")
async def get_user_bookings_details(booking_id: str,
    db: Session = Depends(get_db), current_user = Depends(get_current_user)
):
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {"status": "Success",
             "message": "Booking details successfully fetched", 
            "data": {"booking_details": {
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
    }}}