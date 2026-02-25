from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.room import RoomCreate, RoomResponse
from app.models.roomModel import Room
from app.models.hotelModel import Hotel
from app.models.inventoryModel import Inventory
from app.db.session import SessionLocal
from app.core.security import get_current_user
import uuid

