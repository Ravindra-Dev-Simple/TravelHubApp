from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.hotels import HotelCreate, HotelResponse, HotelListResponse
from app.models.hotelModel import Hotel
from app.db.session import SessionLocal
from app.core.security import get_current_user
from app.core.logger import get_logger
import uuid
from app.models.usersModel import User

logger = get_logger()
router = APIRouter(prefix="/hotels", tags=["Hotels"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create_hotel", response_model=HotelResponse)
async def create_hotel(
    data: HotelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(f"Hotel creation attempt by user {current_user.id}: {data.name}")
    if current_user.role != "admin":
        logger.warning(f"Unauthorized hotel creation attempt by user {current_user.id}")
        raise HTTPException(status_code=403, detail={"status": "Fail" ,"message": "Only owners can create hotels"})

    owner = db.query(User).filter(User.id == current_user.id).first()

    if not owner:
        raise HTTPException(status_code=400, detail="Invalid owner")

    hotel = Hotel(
        id=str(uuid.uuid4()),
        owner_id=current_user.id,
        name=data.name,
        description=data.description,
        latitude = data.latitude,
        longitude = data.longitude,
        amenities = data.amenities,
        city=data.city,
        address=data.address
    )

    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    
    logger.info(f"Hotel created successfully: {hotel.id} - {hotel.name}")

    return hotel


@router.get("/", response_model=HotelListResponse)
async def list_hotels(
    city: str | None = None,
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching hotels list, city filter: {city}")
    query = db.query(Hotel).filter(Hotel.is_active == True)

    if city:
        query = query.filter(Hotel.city == city)
    
    hotels = query.all()
    logger.info(f"Returned {len(hotels)} hotels")
    return {"status": "Success","message": "Updated successfully", "data": hotels}

@router.patch("/update_hotel/{hotel_id}")
async def update_hotel(
    hotel_id: str,
    data: HotelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    hotel.name = data.name
    hotel.description = data.description
    hotel.city = data.city
    hotel.address = data.address
    hotel.latitude = data.latitude
    hotel.longitude = data.longitude
    hotel.amenities = data.amenities
    print(hotel.amenities)
    db.commit()
    return {"status": "Success","message": "Updated successfully"}


@router.post("/detele_hotel/{hotel_id}")
async def delete_hotel(
    hotel_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    hotel.is_active = False
    db.commit()

    return {"message": "Hotel deleted"}

