from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.room import RoomCreate, RoomResponse
from app.schemas.inventory import InventoryCreate, InventoryResponse
from app.schemas.room import UpdateRoomPrice
from app.models.roomModel import Room
from app.models.hotelModel import Hotel
from app.models.inventoryModel import Inventory
from app.db.session import SessionLocal
from app.core.security import get_current_user
import uuid

router = APIRouter(prefix="/rooms", tags=["Rooms"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from datetime import date, timedelta
import uuid

def generate_inventory_for_room(db: Session, room: Room):
    from datetime import date, timedelta
    import uuid

    for i in range(30):
        inventory = Inventory(
            id=str(uuid.uuid4()),
            room_id=room.id,
            date=date.today() + timedelta(days=i),
            available_count=room.total_rooms,
            price=room.base_price
        )
        db.add(inventory)



@router.post("/CreateHotelRoom", response_model=RoomResponse)
async def create_room(
    data: RoomCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    hotel = db.query(Hotel).filter(Hotel.id == data.hotel_id).first()
    if not hotel:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "message": "Hotel Not Found"}
        )

    
    room = Room(
        id=str(uuid.uuid4()),
        hotel_id=data.hotel_id,
        room_type=data.room_type,
        base_price=data.base_price,
        total_rooms=data.total_rooms,
        max_guests=data.max_guests
    )

    db.add(room)
    db.flush()   # 🔥 Important (gets room.id without commit)

    # Generate inventory AFTER room exists
    generate_inventory_for_room(db, room)

    db.commit()
    db.refresh(room)

    return room


@router.get("/GetHotelRooms/{hotel_id}", response_model=list[RoomResponse])
async def get_rooms(hotel_id: str, db: Session = Depends(get_db)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail={"status": "error", "message": "Hotel Not Found"})
    return db.query(Room).filter(Room.hotel_id == hotel_id).all()


@router.put("/UpdateRoomPrice" )
async def update_price(data: UpdateRoomPrice, db: Session = Depends(get_db), current_user = Depends(get_current_user)
):
    db.query(Inventory).filter(
        Inventory.room_id == data.room_id,
        Inventory.date.between(data.start_date, data.end_date)
    ).update(
        {"price": data.new_price},
        synchronize_session=False
    )

    db.commit()

    return {"message": "Price updated"}

@router.get("/HotelRoomAvailability/{room_id}", response_model=list[InventoryResponse])
async def get_inventory(room_id: str, db: Session = Depends(get_db)):
    return db.query(Inventory).filter(
        Inventory.room_id == room_id
    ).all()

