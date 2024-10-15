from sqlalchemy.orm import Session
from app.models.models import Counter
from app.schemas.schemas import CounterCreate
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

def create_counter(db:Session,counter_data:CounterCreate):
    try:
        if counter_data.counter <0:
            raise HTTPException(status_code=400,detail="Counter number must be in positive")
        
        existing_counter_query = text("SELECT * FROM counters WHERE counter = :counter")
        existing_counter =db.execute(existing_counter_query,{"counter":counter_data.counter}).fetchone()

        if existing_counter:
            raise HTTPException(status_code=400,detail = "Counter already exists.")
        
        query=text("INSERT INTO counters (counter) VALUES (:counter) RETURNING id,counter")
        result=db.execute(query,{"counter":counter_data.counter})
        db.commit()
        counter_row = result.fetchone()
        if not counter_row:
            raise HTTPException(status_code=400, detail="Counter creation failed.")
        
        return Counter(id=counter_row.id,counter=counter_row.counter)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error while creating counter: {str(e)}")

def get_all_counter(db:Session):
    try:
        query = text("SELECT * FROM counters")
        result = db.execute(query)
        counters = result.fetchall()
        if not counters:
            raise HTTPException(status_code=400,detail="No counters available")
        return [Counter(id=row.id,counter=row.counter) for row in counters]
    except  SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail=f"Database error while fetching the counter {e}")
