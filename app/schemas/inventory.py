from pydantic import BaseModel
from datetime import date

class InventoryCreate(BaseModel):
    room_id: str
    date: date
    available_count: int
    price: float


class InventoryResponse(BaseModel):
    id: str
    room_id: str
    date: date
    available_count: int
    price: float

    class Config:
        from_attributes = True
