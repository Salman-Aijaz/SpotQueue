from fastapi import FastAPI
from app.db.database import init_db, get_db
from sqlalchemy.orm import Session
from app.routing.service_router import router

app = FastAPI()

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    init_db() 

@app.get("/")
async def root():
    return {"message": "Spot Queue"}
