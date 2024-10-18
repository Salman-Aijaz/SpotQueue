from fastapi import APIRouter,HTTPException,Depends
from sqlalchemy.orm import Session
from app.crud.services_management import create_services,get_all_services,get_service_by_name
from app.schemas.service_schemas import ServiceResponse,ServiceCreate
from app.db.database import get_db

router = APIRouter()
    

@router.post("/",response_model=ServiceResponse)
def create_service(service:ServiceCreate,db:Session=Depends(get_db)):
    """
        Create a new service.

        - **service**: The service details (name, description, etc.)
    
        Returns the newly created service. 
    """
    try:
        db_service = create_services(db,service)
        return db_service
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error creating Service {e}")
    
@router.get("/",response_model=list[ServiceResponse])
def read_services(db:Session=Depends(get_db)):
    """
        Retrieve a list of all available services.

        - Returns a list of all services.
    """
    try:
        services = get_all_services(db) 
        return services
    except Exception as e:
        raise HTTPException(status_code=e.status_code,detail=e.detail)
    
@router.get("/{service_name}",response_model=ServiceResponse)
def read_service_by_name(service_name:str,db:Session = Depends(get_db)):
    """
        Retrieve a service by its name.

        - **service_name**: The name of the service to be fetched.

        Returns the service with the specified name.
    """
    try:
        service = get_service_by_name(db,service_name)
        return service
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code,detail=e.detail)   