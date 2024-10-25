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
from app.core.config import settings

def create_token_record(db: Session, token_data: TokenCreate, duration_text: str, distance_text: str):
    """
        Create a new token record in the database.

        - **db**: The database session used to execute queries.
        - **token_data**: A `TokenCreate` object containing user and service details.
        - **duration_text**: A string representing the duration for which the token is valid.
        - **distance_text**: A string representing the distance from the service location.

        Logic:
        - Generates a unique token number based on the maximum existing token number in the database.
        - Checks how many tokens already exist for the given service and counter, determining the queue position.
        - Validates the user's coordinates against the fixed service coordinates.
        - Creates and commits a new token record to the database.

        Returns:
        - The newly created token object.

        Error Handling:
        - Raises a 500 error for any SQLAlchemy-related issues during the database transaction.
        - Raises a 500 error for any unexpected exceptions.
    """
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

        # Check if the user's coordinates match the fixed service coordinates
        service_latitude, service_longitude = settings.FIXED_COORDINATES[0], settings.FIXED_COORDINATES[1]
        exact_location_match = (float(token_data.latitude) == service_latitude) and (float(token_data.longitude) == service_longitude)
        
        if exact_location_match:
            reach_out = True
        else:
            reach_out = float(distance_text) < 2 or int(duration_text) < 2  # Adjust as needed for your unit

        new_token = Token(
            token_number=new_token_number,  # Increment the max token number
            user_id=token_data.user_id,
            service_id=token_data.service_id,
            counter_id=token_data.counter_id,
            latitude=token_data.latitude,
            longitude=token_data.longitude,
            queue_position=queue_position,
            distance = distance_text,
            duration=duration_text,
            reach_out=reach_out,
            work_status="pending"
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
    """
        Generate a token based on user request.

        - **request**: A `TokenRequest` object containing user and service information.
        - **db**: The database session used to execute queries.

        Logic:
        - Retrieves the user by email from the database.
        - Fetches the service by name.
        - Obtains the counter ID associated with the service.
        - Calculates distance and duration to the service location.
        - Creates a new token record using `create_token_record`.

        Returns:
        - The created token object.

        Error Handling:
            - Raises a 400 error if the user or service is not found.
            - Raises a 500 error for any unexpected exceptions during token generation.
    """
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
    """
        Retrieve all tokens associated with a specific counter ID.

        - **counter_id**: The ID of the counter for which tokens are being retrieved.
        - **db**: The database session used to execute queries.

        Logic:
            - Executes a query to fetch all tokens related to the specified counter ID.

        Returns:
            - A list of tokens if found, otherwise returns None.

        Error Handling:
            - Raises a 500 error for any SQLAlchemy-related issues during the query.
            - Raises a 500 error for any unexpected exceptions.
    """
    try:
        result= db.execute(select(Token).filter(Token.counter_id == counter_id)).scalars().all()
        if not result:
            return None
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error occurred: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching tokens: {e}")

def get_token_by_user_id(db:Session,user_id:int):
    """
        Retrieve the token associated with a specific user ID.

        - **db**: The database session used to execute queries.
        - **user_id**: The ID of the user whose token is being retrieved.

        Logic:
            - Executes a query to fetch the token related to the specified user ID.

        Returns:
            - The token if found, otherwise returns None.

        Error Handling:
            - Raises a 500 error for any SQLAlchemy-related issues during the query.
            - Raises a 500 error for any unexpected exceptions.
    """

    try:
        return db.query(Token).filter(Token.user_id==user_id).first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail=f"Database Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"An unexpected error occurred {e}")

def update_token_distance_duration(db:Session,token:Token,latitude:float,longitude:float, duration_value: int, distance_value: int):
    """
        Update the distance and duration for an existing token.

        - **db**: The database session used to execute queries.
        - **token**: The token object to be updated.
        - **latitude**: The new latitude to be set for the token.
        - **longitude**: The new longitude to be set for the token.
        - **duration_value**: The new duration value to be set for the token.
        - **distance_value**: The new distance value to be set for the token.

        Logic:
            - Updates the token's latitude, longitude, duration, and distance fields.
            - Commits the changes to the database.

        Returns:
            - The updated token object.

        Error Handling:
            - Raises a 500 error for any SQLAlchemy-related issues during the update.
            - Raises a 500 error for any unexpected exceptions.
    """
    try:
        token.latitude=latitude
        token.longitude = longitude
        token.duration = duration_value
        token.distance= distance_value

        db.commit()
        db.refresh(token)
        return token
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Database error {e}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"An unexpected error occurred {e}")
    
def check_reach_out(latitude: float, longitude: float, distance: int, duration: int) -> bool:
    """
        Check if the user is in reach of the service based on their coordinates, distance, and duration.

            - **latitude**: The latitude of the user's location.
            - **longitude**: The longitude of the user's location.
            - **distance**: The distance from the service location.
            - **duration**: The duration of the user's travel.

            Logic:  
            - Validates the latitude and longitude values to ensure they are within valid ranges.
            - Validates that distance and duration are both non-negative.
            - Determines if the user is within reach based on predefined thresholds.

            Returns:
            - True if the user is considered to be in reach; False otherwise.

            Error Handling:
                - Raises a ValueError for invalid coordinate values.
    """
    try:
        # Validate latitude and longitude (example: check if they are within valid GPS ranges)
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid latitude or longitude values.")

        # Validate distance and duration (example: they should be non-negative)
        if distance < 0 or duration < 0:
            raise HTTPException(status_code=400, detail="Distance and duration must be non-negative.")
        
        service_coordinate = (settings.FIXED_COORDINATES[0], settings.FIXED_COORDINATES[1])
        user_at_service_location = (latitude, longitude) == service_coordinate
        return user_at_service_location and (distance < 2) and (duration < 2)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Unexpected error occurred: {e}")
