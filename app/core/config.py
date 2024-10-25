import os 
from dotenv import load_dotenv
from fastapi.testclient import TestClient
import zoneinfo
from app.main import app
import logging

load_dotenv()

class Settings:
    DATABASE_URL =os.getenv("DATABASE_URL")
    DISTANCE_MATRIX_API_KEY=os.getenv("DISTANCE_MATRIX_API_KEY")
    client = TestClient(app)
    SECRET_KEY=os.getenv("SECRET_KEY")
    ALGORITHM=os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    UTC=zoneinfo.ZoneInfo("UTC")
    logging.basicConfig(level=logging.INFO) 
    logger= logging.getLogger(__name__)
    FIXED_COORDINATES = (24.8523464, 67.0078039)  # Fixed coordinates for both services

settings=Settings()    