
from sqlalchemy.orm import Session
from app.models.counter_models import Counter
from app.schemas.counter_schemas import CounterCreate
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.models.service_models import Service

# 1. Create a new counter
def create_counter(db: Session, counter: CounterCreate):
    try:
        # Get the service_id by service_name
        service = db.query(Service).filter(Service.service_name == counter.service_name).first()
        
        if not service:
            raise HTTPException(status_code=400, detail="Service not found")
        
        # Check if the counter already exists
        existing_counter = db.query(Counter).filter(
            Counter.counter_number == counter.counter_number, 
            Counter.service_id == service.id  # Use service.id instead of counter.service_id
        ).first()
        
        if existing_counter:
            raise HTTPException(status_code=400, detail="Counter already exists")

        new_counter = Counter(counter_number=counter.counter_number, service_id=service.id, user_id=counter.user_id)
        db.add(new_counter)
        db.commit()
        db.refresh(new_counter)
        return new_counter
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error while creating counter: {e}")

# 2. Retrieve all counters
def get_all_counters(db: Session):
    try:
        counters = db.query(Counter).all()
        if not counters:
            raise HTTPException(status_code=404, detail="No counters available")
        return counters
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error while fetching counters: {e}")

# 3. Retrieve a counter by ID
def get_counter_by_id(db: Session, counter_id: int):
    try:
        counter = db.query(Counter).filter(Counter.id == counter_id).first()
        if not counter:
            raise HTTPException(status_code=404, detail="Counter not found")
        return counter
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error while fetching the counter: {e}")
