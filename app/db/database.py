from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
import redis 

# Create SQLAlchemy engine and sessionmaker 
engine = create_engine(settings.DATABASE_URL, echo=True) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Base class for models
Base = declarative_base()

# Optionally, check if Redis is running
try:
    redis_client.ping()
    settings.logger.info("Connected to Redis")
except redis.ConnectionError:
    settings.logger.error("Could not connect to Redis")

# Function to initialize the database with error handling
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        settings.logger.info("Database initialized successfully.")
    except SQLAlchemyError as e:
        settings.logger.error(f"Error initializing the database: {e}")
    except Exception as ex:
        settings.logger.error(f"Unexpected error during database initialization: {ex}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        settings.logger.error(f"Database session error: {e}")
        raise
    except Exception as ex:
        settings.logger.error(f"Unexpected error during database session: {ex}")
        raise
    finally:
        db.close()
        settings.logger.info("Database session closed.")
