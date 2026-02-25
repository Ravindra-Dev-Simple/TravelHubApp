from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os
import certifi

from sqlalchemy.engine import URL

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username="ravindra123",
    password="Aravi@8898",
    host="travelhubdbserver.mysql.database.azure.com",
    port=3306,
    database="airbnbdb",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"ssl": {"ca": certifi.where()}},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

import os
from dotenv import load_dotenv
from alembic import context
from sqlalchemy import engine_from_config, pool

# 1. Load the .env file
load_dotenv()

# 2. Get the URL from environment
db_url = os.getenv("DATABASE_URL")

# 3. Override the alembic.ini config dynamically
# if db_url:
#     config.set_main_option("sqlalchemy.url", db_url)

# ... (keep the rest of the existing file as is)