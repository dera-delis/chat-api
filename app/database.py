from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Use connection pooling with better error handling
# Increased pool size to handle WebSocket connections (which hold sessions) + HTTP requests
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=20,  # Number of connections to maintain (increased for WebSocket connections)
    max_overflow=30,  # Additional connections beyond pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_reset_on_return='rollback',  # Ensure no open transactions remain
    connect_args={"connect_timeout": 10}  # 10 second timeout
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

