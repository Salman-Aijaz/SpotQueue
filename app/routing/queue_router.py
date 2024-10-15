from fastapi import APIRouter,HTTPException,Depends
from sqlalchemy.orm import Session
from app.crud.counter_management import create_counter,get_all_counter
from app.schemas.schemas import CounterCreate,CounterResponse
from app.db.database import get_db

router = APIRouter()

@router.post("/counter",response_model=CounterResponse)
def add_counter(counter:CounterCreate,db:Session = Depends(get_db)):
    try:
        db_counter = create_counter(db,counter)
        return db_counter
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error on create counter function {e}")


@router.get("/counter",response_model=list[CounterResponse])
def read_counter(db:Session=Depends(get_db)):
    try:
        counter = get_all_counter(db)
        if not counter:
            raise HTTPException(status_code=400,detail="No Counter Available")
        return counter
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Error on read counter function {e}")