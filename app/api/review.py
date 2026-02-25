from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.core.security import get_current_user
from app.models.usersModel import User
from app.models.hotelModel import Hotel
from app.models.booking import Booking
from app.models.reviewModel import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.core.logger import get_logger
from sqlalchemy import text
import uuid

logger = get_logger()
router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/create_review", response_model=ReviewResponse)
async def create_review(data: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == data.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    hotel = db.query(Hotel).filter(Hotel.id == data.hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    review = Review(
        id=str(uuid.uuid4()),
        hotel_id=data.hotel_id,
        user_id=current_user.id,
        booking_id=data.booking_id,
        rating=data.rating,
        comment=data.comment
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review created: {review.id} by user {current_user.id}")
    return review


@router.get("/{hotel_id}/reviews", response_model=list[ReviewResponse])
async def get_reviews_by_hotel(hotel_id: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT r.id, u.full_name as user_name, r.hotel_id, r.user_id, r.booking_id, r.rating, r.comment
        FROM tbl_reviews r
        JOIN tbl_users u ON r.user_id = u.id
        WHERE r.hotel_id = :hotel_id
        ORDER BY r.created_at DESC
    """)
    reviews = db.execute(query, {"hotel_id": hotel_id}).fetchall()
    return reviews
