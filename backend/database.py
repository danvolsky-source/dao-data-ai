"""Database Connection and Session Management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from typing import Generator
from models import Base
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")  # PostgreSQL connection string

# Initialize Supabase client
supabase_client: Client = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Warning: Failed to initialize Supabase client: {e}")

# SQLAlchemy database engine
engine = None
SessionLocal = None

try:
    if SUPABASE_DB_URL:
        # Create engine with connection pooling
        engine = create_engine(
            SUPABASE_DB_URL,
            poolclass=NullPool,  # Supabase handles pooling
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,  # Verify connections before using
        )
        
        # Create session factory
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        print("✓ Database engine initialized successfully")
except Exception as e:
    print(f"Warning: Failed to initialize database engine: {e}")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    Usage in FastAPI: def endpoint(db: Session = Depends(get_db))
    """
    if SessionLocal is None:
        raise Exception("Database not configured. Set SUPABASE_DB_URL environment variable.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_supabase() -> Client:
    """
    Get Supabase client instance
    """
    if supabase_client is None:
        raise Exception("Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
    return supabase_client


def init_db():
    """
    Initialize database tables
    Creates all tables defined in models.py
    """
    if engine is None:
        print("Warning: Cannot initialize database - engine not configured")
        return
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")


if __name__ == "__main__":
    print("Database Module")
    print(f"Supabase URL configured: {bool(SUPABASE_URL)}")
    print(f"Supabase DB URL configured: {bool(SUPABASE_DB_URL)}")
    
    if engine:
        print("\nInitializing database tables...")
        init_db()
