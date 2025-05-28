from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "postgresql://uday:1234@localhost:5432/fast_api"

engine = create_engine(DATABASE_URL)  # Sync engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)