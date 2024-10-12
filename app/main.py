from fastapi import FastAPI
from app.db.database import init_db, get_db
from sqlalchemy.orm import Session

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db() 

@app.get("/")
async def root():
    return {"message": "Spot Queue"}
