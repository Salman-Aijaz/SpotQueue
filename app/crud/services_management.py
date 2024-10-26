from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.service_models import Service
from app.schemas.service_schemas import ServiceCreate
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings

# 1. Create a new service
def create_services(db:Session,service:ServiceCreate):
    """
        Create a new service in the database.
    
        - **db**: The database session used to execute queries.
        - **service**: A `ServiceCreate` object containing service details like name, entry time, end time, and the number of counters.

        Logic:
        - First, it checks if a service with the same name already exists using a SQL query.
        - If a service exists, it raises a 400 HTTPException to avoid duplicates.
        - It ensures that the number of counters is greater than zero. If not, a 400 HTTPException is raised.
        - If all validations pass, it inserts the new service into the database and returns the created service details.
    
        Returns:
        - A dictionary containing the service ID, name, entry time, end time, and number of counters.

        Error Handling:
        - Raises a 400 error if the service already exists or the number of counters is invalid.
        - Raises a 500 error for any SQLAlchemy-related issues during the database transaction.
    """
    try:
        settings.logger.info(f"Checking if service '{service.service_name}' already exists.")
        query_check = text("""
            SELECT id FROM services WHERE service_name = :service_name""")
        result_check= db.execute(query_check,{"service_name":service.service_name})

        existing_services= result_check.fetchone()

        if existing_services:
            settings.logger.warning(f"Service '{service.service_name}' already exists.")
            raise HTTPException(status_code=400,detail="Service already exists")
        
        query = text("""
        INSERT INTO services (service_name,service_entry_time,service_end_time, number_of_counters)
        VALUES (:service_name, :service_entry_time, :service_end_time, :number_of_counters)
        RETURNING id, service_name, service_entry_time, service_end_time, number_of_counters             
        """)
        settings.logger.info(f"Inserting service '{service.service_name}' into database.")

        result=db.execute(query,{
            "service_name":service.service_name,
            "service_entry_time":service.service_entry_time,
            "service_end_time":service.service_end_time,
            "number_of_counters":service.number_of_counters
        })

        db.commit()

        created_service = result.fetchone()

        if create_services is None:
            settings.logger.error("Service creation failed; no result returned.")
            raise HTTPException(status_code=400,detail="Service not created")    
        
        settings.logger.info(f"Service '{created_service.service_name}' created successfully.")
        return {
            "id": created_service.id,
            "service_name": created_service.service_name,
            "service_entry_time": created_service.service_entry_time,
            "service_end_time": created_service.service_end_time,
            "number_of_counters": created_service.number_of_counters
        }
    except SQLAlchemyError as e:
        db.rollback()
        settings.logger.exception(f"SQLAlchemyError occurred during service creation {e}.") 
        raise HTTPException(status_code=500, detail=f"Error while creating service: {e}")

# 2. Retrieve all services
def get_all_services(db: Session):
    """
        Fetch all services from the database.
    
        - **db**: The database session used to execute queries.

        Logic:
        - Queries the `services` table to retrieve all available services.
        - If no services are found, it raises a 400 HTTPException.

        Returns:
        - A list of all available services.
    
        Error Handling:
        - Raises a 400 error if no services are found.
        - Raises a 500 error for any SQLAlchemy-related issues during the query.
    """
    try:
        settings.logger.info("Fetching all services from the database.")
        query = db.query(Service).all()  
        if not query:
            settings.logger.warning("No services found in the database.")
            raise HTTPException(status_code=400, detail="No Service available")
        settings.logger.info(f"Retrieved {len(query)} services from the database.")
        return query 
    except SQLAlchemyError as e:
        settings.logger.exception(f"SQLAlchemyError occurred while retrieving all services {e}.")
        raise HTTPException(status_code=500, detail=f"Error while fetching the services {e}")

# 3. Retrieve a service by name
def get_service_by_name(db:Session,service_name:str):
    """
        Fetch a service by its name from the database.
    
        - **db**: The database session used to execute queries.
        - **service_name**: The name of the service to search for.

        Logic:
        - Executes a SQL query to find the service with the given name.
        - If the service is not found or exist, it raises a 400 HTTPException.

        Returns:
        - A dictionary containing the service's ID, name, entry time, end time, and number of counters.

        Error Handling:
        - Raises a 400 error if the service is not found or exist.
        - Raises a 500 error for any SQLAlchemy-related issues during the query.
    """
    try:
        settings.logger.info(f"Fetching service '{service_name}' by name.")
        query=text("""
            SELECT id,service_name,service_entry_time,service_end_time
            FROM services
            WHERE service_name = :service_name
        """)

        result = db.execute(query,{'service_name': service_name})
        service = result.fetchone()

        if service is None:
            settings.logger.warning(f"Service '{service_name}' not found.")
            raise HTTPException(status_code=400,detail=f"Service '{service_name}' not found or exist")
        
        settings.logger.info(f"Service '{service_name}' found with ID {service.id}.")

        return {
            "id": service.id,
            "service_name": service.service_name,
            "service_entry_time": service.service_entry_time,
            "service_end_time": service.service_end_time,
        }
    except SQLAlchemyError as e:
        settings.logger.exception(f"SQLAlchemyError occurred while fetching the service by name {e}.")
        raise HTTPException(status_code=500, detail=f"Error while fetching the service: {e}")
