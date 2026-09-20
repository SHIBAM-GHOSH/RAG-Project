# test_mysql_connection.py
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Build the engine from the URL in .env
engine = create_engine(os.getenv("DATABASE_URL"))

# Try a simple query
with engine.connect() as conn:
    version = conn.execute(text("SELECT VERSION()")).scalar()
    print("✅ Connected! MySQL version →", version)
