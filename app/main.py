from fastapi import Depends, FastAPI, Request
from app.api.routers.routers import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.middleware import LoggingMiddleware
from app.core.logger import get_logger
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

logger = get_logger()

# prefix="/" + os.getenv("UsePathBase","")

from apscheduler.schedulers.background import BackgroundScheduler
from app.background.booking_expire import expire_bookings

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting TravelHub API...")
    scheduler.add_job(expire_bookings, "interval", minutes=1)
    scheduler.start()
    logger.info("Background scheduler started")
    logger.info("API startup complete")
    yield
    # Shutdown
    logger.info("API shutting down")
    scheduler.shutdown()


app = FastAPI(title="TravelHub API", version="1.0.0", lifespan=lifespan)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
