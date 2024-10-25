
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.counter_schemas import CounterCreate, CounterResponse,NextPersonRequest
from app.crud.counter_management import create_counter, get_all_counters, get_counter_by_id, process_next_person
from fastapi import HTTPException

router = APIRouter()

@router.post("/", response_model=CounterResponse)
def add_counter(counter: CounterCreate, db: Session = Depends(get_db)):
    try:
        return create_counter(db, counter)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error creating Counter {e}")

@router.get("/", response_model=list[CounterResponse])
def list_counters(db: Session = Depends(get_db)):
    try:
        return get_all_counters(db)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error getting Counter {e}")

@router.get("/{counter_id}", response_model=CounterResponse)
def get_counter(counter_id: int, db: Session = Depends(get_db)):
    try:
        return get_counter_by_id(db, counter_id)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error getting Counter by his id {e}")


@router.post("/next-person")
async def next_person(request: NextPersonRequest, db: Session = Depends(get_db)):
    try:
        return await process_next_person(request.user_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing next person: {e}")