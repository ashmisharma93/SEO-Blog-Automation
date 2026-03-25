from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings
from sqlalchemy.orm import Session

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={'check_same_thread': False}
)

# Create session
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)

# Base class for models
Base = declarative_base()

'''
engine -> connects to database
SessionLocal -> allows DB operations
Base -> parent class for all tables

'''

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

