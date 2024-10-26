from fastapi.testclient import TestClient
from app.main import app
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Tuple, ClassVar
import logging
import zoneinfo

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DISTANCE_MATRIX_API_KEY: str = Field(..., env="DISTANCE_MATRIX_API_KEY")
    client = TestClient(app)
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(..., env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 30
    UTC: ClassVar=zoneinfo.ZoneInfo("UTC")
    logging.basicConfig(level=logging.INFO) 
    logger: ClassVar= logging.getLogger(__name__)
    FIXED_COORDINATES: Tuple[float, float] = (24.8523464, 67.0078039) # Fixed coordinates for both services

    @field_validator("FIXED_COORDINATES")
    def validate_coordinates(cls, v):
        if not (isinstance(v, tuple) and len(v) == 2):
            raise ValueError("FIXED_COORDINATES must be a tuple with two float values (latitude and longitude).")
        return v

    class Config:
        env_file = ".env"
settings=Settings()    