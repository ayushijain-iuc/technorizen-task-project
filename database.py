from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import logging
import os

logger = logging.getLogger(__name__)
database_url = settings.DATABASE_URL


if "sqlite" in database_url.lower():
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False
    )
    logger.info("Using SQLite database")
else:
    engine = create_engine(
        database_url,
        pool_pre_ping=True, 
        echo=False
    )
    logger.info("Using PostgreSQL database")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
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

