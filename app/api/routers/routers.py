from fastapi import APIRouter
from app.api.users import router as userRouters
from app.api.auth import router as authRouters
from app.api.hotels import router as hotelRouters
from app.api.room import router as roomRouters
from app.api.booking import router as bookingRouters
from app.api.invoice import router as invoiceRouters
from app.api.review import router as reviewRouters

router = APIRouter()
router.include_router(authRouters)
router.include_router(userRouters)
router.include_router(hotelRouters)
router.include_router(roomRouters)
router.include_router(bookingRouters)
router.include_router(invoiceRouters)
router.include_router(reviewRouters)