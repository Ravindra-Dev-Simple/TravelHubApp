from pydantic import BaseModel
from typing import Optional

class RoomCreate(BaseModel):
    hotel_id: str
    room_type: str
    base_price: float
    total_rooms: int
    max_guests: Optional[int] = 2


class RoomResponse(BaseModel):
    id: str
    hotel_id: str
    room_type: str
    base_price: float
    total_rooms: int
    max_guests: int

    class Config:
        from_attributes = True

class UpdateRoomPrice(BaseModel):
    room_id: str
    start_date: str
    end_date: str
    new_price: float