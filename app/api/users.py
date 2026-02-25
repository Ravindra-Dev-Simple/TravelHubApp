from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user, Depends,Session
from app.schemas.users import UserResponse
from app.db.dependencies import get_db
from app.models.usersModel import User
from app.schemas.users import UserLogin
from app.services.auth_service import verify_password, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user = Depends(get_current_user)):
    return current_user

@router.patch("/update_user")
async def update_profile(full_name: str, 
                   current_user = Depends(get_current_user),
                   db: Session = Depends(get_db)):

    current_user.full_name = full_name
    db.commit() 
    return {"status": "Success", "message": "Profile updated"}


@router.get("/", response_model=list[UserResponse])
async def list_users(current_user = Depends(get_current_user),
               db: Session = Depends(get_db)):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    return db.query(User).all()


