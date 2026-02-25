from pydantic import BaseModel
from datetime import date


class AvailabilityRequest(BaseModel):
    hotel_id: str
    check_in: date
    check_out: date

class AvailableRoomResponse(BaseModel):
    room_id: str
    room_type: str
    max_guests: int
    total_price: float

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    hotel_id: str
    room_id: str
    check_in: date
    check_out: date
