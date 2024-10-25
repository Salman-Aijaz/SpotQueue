
from sqlalchemy.orm import Session
from app.models.counter_models import Counter
from app.models.token_models import Token
from app.schemas.counter_schemas import CounterCreate
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.models.service_models import Service
from app.db.database import redis_client
import logging

logger = logging.getLogger(__name__)

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

        new_counter = Counter(counter_number=counter.counter_number, service_id=service.id)
        db.add(new_counter)
        db.commit()
        db.refresh(new_counter)
        counters_count = db.query(Counter).filter(Counter.service_id == service.id).count()
        service.number_of_counters = counters_count
        db.commit()
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

def get_counter_by_service_id(db: Session, service_id: int):
    try:
        counter = db.query(Counter).filter(Counter.service_id == service_id).first()
        return counter.id if counter else None  # Return counter id or None if not found
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error in get_counter_by_service_id: {e}")
    
async def process_next_person(user_id: int, db: Session):
    try:
        logger.info(f"Processing next person for user ID: {user_id}")

        # Get the current token for the user
        token = db.query(Token).filter(Token.user_id == user_id).first()
        if not token:
            logger.error(f"User {user_id} not found in the queue.")
            raise HTTPException(status_code=400, detail="User not found in the queue.")
        
        # Mark user's work as completed and clear their queue position
        token.work_status = "completed"
        token.queue_position = 0
        db.commit()
        db.refresh(token)

        logger.info(f"User {user_id}'s work is completed. Queue position set to 0.")

        # Remove user_id from the Redis queue
        redis_client.lrem("user_queue", 0, str(user_id))  # Ensure the user_id is a string
        logger.info(f"User {user_id} removed from Redis queue.")

        # Log the queue after removal
        user_queue = redis_client.lrange("user_queue", 0, -1)
        logger.info(f"Queue after removal: {user_queue}")

        # Decode and clean up user IDs from Redis
        user_queue = [
            int(user_id_str.decode('utf-8'))  # Decode byte strings to integers
            for user_id_str in user_queue
        ]

        # Rearrange queue positions if there are remaining users
        if user_queue:
            for idx, user_id in enumerate(user_queue):
                db_token = db.query(Token).filter(Token.user_id == user_id).first()
                if db_token:
                    new_position = idx + 1
                    db_token.queue_position = new_position  # Assign the new position (1-based index)
                    # Set db_token to expire to ensure refreshed values in db session
                    db.expire(db_token)
                    logger.info(f"Updated user {user_id} to queue position {new_position}")
            db.commit()  # Commit once after all updates
        else:
            logger.info("Queue is empty after removal.")

        return {"message": f"User {user_id} marked completed and queue rearranged."}

    except Exception as e:
        logger.error(f"Error processing user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing next person: {str(e)}")
