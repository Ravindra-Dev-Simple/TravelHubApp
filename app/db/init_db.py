from app.db.base import Base
from app.db.session import engine
import app.models  # import all models

def init():
    Base.metadata.create_all(bind=engine)
