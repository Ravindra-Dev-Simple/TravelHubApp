from pydantic import BaseModel
from typing import Optional, List

class HotelCreate(BaseModel):
    name: str
    description: Optional[str]
    city: str
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    amenities: Optional[List[str]] = []


class HotelResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    city: str
    address: Optional[str]
    latitude: float
    longitude: float
    amenities: Optional[List[str]]

    class Config:
        from_attributes = True

class HotelListResponse(BaseModel):
    status: str
    message: str
    data: List[HotelResponse]

