from common.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.db.base import Base
import time

DATABASE_URL = Config.DATABASE_URL
MAX_RETRIES = 3
RETRY_DELAY = 5

_engine = None


def create_database_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            pool_size=50,
            max_overflow=20,
            pool_pre_ping=True,
        )
    return _engine


def connect_to_database():
    for retry_attempt in range(MAX_RETRIES):
        try:
            engine = create_database_engine()
            Base.metadata.create_all(engine)
            SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine,
            )
            return SessionLocal()
        except Exception as e:
            print(
                f"Database connection attempt {retry_attempt + 1} failed. Error: {str(e)}"
            )
            if retry_attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise


def get_db():
    db = None
    try:
        db = connect_to_database()
        yield db
    finally:
        db.close()
