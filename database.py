from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Get database URL from settings
database_url = settings.DATABASE_URL

# Create database engine
if "sqlite" in database_url.lower():
    # SQLite database
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False
    )
    logger.info("Using SQLite database")
else:
    # PostgreSQL database
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # Verify connections before using
        echo=False
    )
    logger.info("Using PostgreSQL database")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        # Test connection for PostgreSQL
        if "sqlite" not in database_url.lower():
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT current_database(), current_schema()"))
                    row = result.fetchone()
                    logger.info(f"Connected to PostgreSQL database: {row[0]}, schema: {row[1]}")
            except Exception as conn_err:
                logger.error(f"Failed to connect to PostgreSQL: {conn_err}")
                logger.error("Please check:")
                logger.error("1. Internet connection")
                logger.error("2. Supabase project is active")
                logger.error("3. Connection string is correct")
                logger.error("4. Firewall/network settings")
                raise
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
        
        # Verify tables were created (for PostgreSQL)
        if "sqlite" not in database_url.lower():
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """))
                    tables = [row[0] for row in result.fetchall()]
                    logger.info(f"Tables in database: {', '.join(tables) if tables else 'None'}")
                    if not tables:
                        logger.warning("No tables found in database after creation!")
                    else:
                        logger.info(f"Successfully created/verified {len(tables)} tables")
            except Exception as verify_err:
                logger.warning(f"Could not verify tables: {verify_err}")
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        if "sqlite" not in database_url.lower():
            logger.warning("PostgreSQL connection failed. Check internet connection and Supabase credentials.")
        raise

