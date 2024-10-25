import os 
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from app.main import app

load_dotenv()

class Settings:
    DATABASE_URL =os.getenv("DATABASE_URL")
    DISTANCE_MATRIX_API=os.getenv("DISTANCE_MATRIX_API")
    client = TestClient(app)


settings=Settings()    