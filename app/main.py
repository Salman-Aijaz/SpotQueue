from fastapi import FastAPI
from app.routing.service_router import router as service_router
from app.routing.user_router import router as user_router
from app.db.database import init_db
from app.routing.counter_routes import router as counter_router
import asyncio

async def lifespan(app:FastAPI):
    await asyncio.sleep(0.1)
    init_db() 
    yield

app:FastAPI = FastAPI(lifespan=lifespan)

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(service_router, prefix="/services", tags=["Services"])
app.include_router(counter_router,prefix="/counter",tags=["counters"])