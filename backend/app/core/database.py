"""backend/app/core/database.py"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ----------------------------------------------------------------------
# Load .env automatically – fastapi projects usually have python-dotenv installed
# ----------------------------------------------------------------------
from dotenv import load_dotenv

load_dotenv()  # pulls variables from .env into os.environ

# ----------------------------------------------------------------------
# Connection URL – default to SQLite only if DATABASE_URL is missing
# ----------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./study_rag.db"


# ----------------------------------------------------------------------
# Engine creation – MySQL needs no special kwargs; SQLite needs check_same_thread
# ----------------------------------------------------------------------
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    # MySQL (pymysql) – default parameters are fine
    engine = create_engine(DATABASE_URL)

# ----------------------------------------------------------------------
# Session factory
# ----------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ----------------------------------------------------------------------
# Base class for ORM models
# ----------------------------------------------------------------------
Base = declarative_base()


# ----------------------------------------------------------------------
# FastAPI dependency that yields a DB session per request
# ----------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
