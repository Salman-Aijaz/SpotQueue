import os 
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL =os.getenv("DATABASE_URL")
    DISTANCE_MATRIX_API=os.getenv("DISTANCE_MATRIX_API")


settings=Settings()    