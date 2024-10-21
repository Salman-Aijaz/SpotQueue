from app.crud.counter_management import get_counter_by_service_id
from app.crud.services_management import get_service_by_name
from app.crud.user_management import get_user_by_email
from app.models.token_models import Token
from app.schemas.token_schemas import TokenCreate, TokenRequest
from sqlalchemy.orm import Session
from sqlalchemy import func,select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.utils.get_distance import get_distance

def create_token_record(db: Session, token_data: TokenCreate, duration_text: str, distance_text: str):
    try:
        # Generate a unique token number based on the maximum existing token_number
        token_number = db.query(func.max(Token.token_number)).scalar() or 0
        max_token_number = int(token_number) if token_number is not None else 0
        new_token_number = max_token_number + 1


        existing_token_count = db.query(Token).filter(
            Token.service_id == token_data.service_id,
            Token.counter_id == token_data.counter_id,
        ).count()

        queue_position = existing_token_count+1
        new_token = Token(
            token_number=new_token_number,  # Increment the max token number
            user_id=token_data.user_id,
            service_id=token_data.service_id,
            counter_id=token_data.counter_id,
            latitude=token_data.latitude,
            longitude=token_data.longitude,
            queue_position=queue_position,
            distance = distance_text,
            duration=duration_text
        )
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        return new_token
    except SQLAlchemyError as e:
        db.rollback() 
        raise HTTPException(status_code=500,detail=f"Database error occurred: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    


async def generate_token(request: TokenRequest, db: Session):
    try:
        # Get user by email
        user = get_user_by_email(db, request.email)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        # Get service by name
        service = get_service_by_name(db, request.service_name)
        if not service:
            raise HTTPException(status_code=400, detail="Service not found")

        # Access the service ID from the dictionary
        service_id = service["id"]

        # Get counter responsible for this service
        counter_id = get_counter_by_service_id(db, service_id)
        if counter_id is None:
            raise HTTPException(status_code=400, detail="No counter available for this service")

        duration_text, distance_text = await get_distance(request.latitude, request.longitude)

        # Generate the token and store it in the database
        token_data = TokenCreate(
            user_id=user.id,
            service_id=service_id,
            counter_id=counter_id,  
            latitude=request.latitude,
            longitude=request.longitude
        )

        token = create_token_record(db, token_data,duration_text, distance_text)

        return token
    
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while generating token: {e}")


def get_token_by_counter_id(counter_id:int,db:Session):
    try:
        result= db.execute(select(Token).filter(Token.counter_id == counter_id)).scalars().all()
        if not result:
            return None
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching tokens: {e}")
