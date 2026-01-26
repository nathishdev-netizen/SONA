from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.db.models import Base

# Sync Engine (for now, simpler for current codebase)
engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
