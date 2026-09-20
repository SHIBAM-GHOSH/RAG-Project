# create_mysql_tables.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# --------------------------------------------------------------
# Load variables from .env (so we pick up DATABASE_URL)
# --------------------------------------------------------------
load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL not found in .env")

# --------------------------------------------------------------
# Build the SQLAlchemy engine for MySQL
# --------------------------------------------------------------
engine = create_engine(db_url)

# --------------------------------------------------------------
# Import all ORM models so they register with Base.metadata
# --------------------------------------------------------------
# This import has side‑effects: it defines ProjectModel,
# DocumentModel, SessionModel and attaches them to Base.
from backend.app.models import db_models  # noqa: F401

# --------------------------------------------------------------
# Create the tables (if they don't already exist)
# --------------------------------------------------------------
from backend.app.core.database import Base
Base.metadata.create_all(bind=engine)

print("✅ Tables have been created (or already existed) in MySQL database 'study_rag'.")

