
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.counter_schemas import CounterCreate, CounterResponse,NextPersonRequest
from app.crud.counter_management import create_counter, get_all_counters, get_counter_by_id, process_next_person
from fastapi import HTTPException

router = APIRouter()

@router.post("/", response_model=CounterResponse)
def add_counter(counter: CounterCreate, db: Session = Depends(get_db)):
    """
        Add a new counter to the system.

        This endpoint creates a new counter, associating it with a service. The counter details, 
        including counter number and service name, are provided in the request body.

        Parameters:
            - counter (CounterCreate): The counter details, containing:
                - counter_number (int): Unique identifier number for the counter.
                - service_name (str): Name of the service the counter is associated with.
            - db (Session, optional): The database session. Defaults to a dependency from `get_db`.

        Raises:
            - HTTPException: Raised if an error occurs during counter creation (status code 500).

        Returns:
            - CounterResponse: The response object with the created counter’s information:
                - id (int): Unique ID of the counter.
                - counter_number (int): The counter's number.
                - service_id (int): ID of the service the counter is linked to.
    """
    try:
        return create_counter(db, counter)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error creating Counter {e}")

@router.get("/", response_model=list[CounterResponse])
def list_counters(db: Session = Depends(get_db)):
    """
        Retrieve a list of all counters.

        This endpoint returns all counters in the system, with each counter’s number and 
        associated service ID.

        Parameters:
            - db (Session, optional): The database session. Defaults to a dependency from `get_db`.

        Raises:
            - HTTPException: Raised if an error occurs while retrieving counters (status code 500).

        Returns:
            - list[CounterResponse]: A list of counter objects, each containing:
                - id (int): Unique identifier of the counter.
                - counter_number (int): Number assigned to the counter.
                - service_id (int): ID of the service the counter is associated with.
    """
    try:
        return get_all_counters(db)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error getting Counter {e}")

@router.get("/{counter_id}", response_model=CounterResponse)
def get_counter(counter_id: int, db: Session = Depends(get_db)):
    """
        Retrieve a specific counter by its ID.

        This endpoint provides information about a specific counter based on its unique ID.

        Parameters:
            - counter_id (int): The unique ID of the counter to retrieve.
            - db (Session, optional): The database session. Defaults to a dependency from `get_db`.

        Raises:
            - HTTPException: Raised if an error occurs while retrieving the counter (status code 500).

        Returns:
            - CounterResponse: The counter’s details, including:
                - id (int): Unique identifier of the counter.
                - counter_number (int): Number assigned to the counter.
                - service_id (int): ID of the service the counter is associated with.
    """
    try:
        return get_counter_by_id(db, counter_id)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error getting Counter by his id {e}")


@router.post("/next-person")
async def next_person(request: NextPersonRequest, db: Session = Depends(get_db)):
    """
        Process the next person in line for a service.

        This endpoint processes the next person in the queue based on the provided user ID. 
        It facilitates managing the flow of users in the queue and advancing the queue order.

        Parameters:
            - request (NextPersonRequest): Contains user ID details for the person to be processed next.
            - db (Session, optional): The database session, obtained as a dependency from `get_db`.

        Raises:
            - HTTPException: Raised if an error occurs while processing the next person (status code 500).

        Returns:
            - JSON response with details of the next person processed.
    """
    try:
        return await process_next_person(request.user_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing next person: {e}")