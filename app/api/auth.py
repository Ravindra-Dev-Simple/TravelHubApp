from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.schemas.users import UserCreate, UserLogin
from app.models.usersModel import User
from app.schemas.auth import Login, LoginResponse
from app.db.session import SessionLocal
from app.models.auth import RefreshToken
from app.services.auth_service import create_access_token, hash_password, verify_password, create_refresh_token, hash_token, REFRESH_TOKEN_EXPIRE_DAYS
from app.core.logger import get_logger
import uuid
from datetime import datetime, timedelta

logger = get_logger()
router = APIRouter(prefix="/auth", tags=["Auth"])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt for email: {user.email}")
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        logger.warning(f"Registration failed - Email already exists: {user.email}")
        raise HTTPException(status_code=400, detail={"message": "mail already registered"})

    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        password_hash=hash_password(user.password),
        full_name=user.full_name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"User registered successfully: {user.email}")

    return {"status": "success",
        "message": "User created successfully"}


@router.post("/login", response_model=LoginResponse)
def login(
    data: Login,
    response: Response,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    db_token = RefreshToken(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    db.add(db_token)
    db.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

