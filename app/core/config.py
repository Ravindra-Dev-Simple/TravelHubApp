from pydantic_settings import BaseSettings
import os
from pathlib import Path

# Get the app directory path
APP_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "your-secret-key-change-in-production"

    class Config:
        env_file = os.path.join(APP_DIR, ".env")
        env_file_encoding = 'utf-8'

settings = Settings()
