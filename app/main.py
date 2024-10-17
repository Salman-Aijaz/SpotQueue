from fastapi import FastAPI
from app.routing.service_router import router
from app.db.database import init_db

async def lifespan(app:FastAPI):
    init_db() 
    yield

app:FastAPI = FastAPI(lifespan=lifespan)
app.include_router(router)