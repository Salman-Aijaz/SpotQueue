import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine and sessionmaker 
engine = create_engine(settings.DATABASE_URL, echo=True) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Function to initialize the database with error handling
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing the database: {e}")
    except Exception as ex:
        logger.error(f"Unexpected error during database initialization: {ex}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        raise
    except Exception as ex:
        logger.error(f"Unexpected error during database session: {ex}")
        raise
    finally:
        db.close()
        logger.info("Database session closed.")
