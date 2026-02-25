from pydantic import BaseModel

class UserBasic(BaseModel):
    id: str
    name: str  # or username

class ReviewCreate(BaseModel):
    hotel_id: str
    user_id: str
    booking_id: str
    rating: int
    comment: str | None = None

class ReviewResponse(BaseModel):
    id: str
    hotel_id: str
    user_id: str    
    booking_id: str
    rating: int
    comment: str
    user_name: str  # Change from 'user' to 'user_name'

    class Config:
        from_attributes = True