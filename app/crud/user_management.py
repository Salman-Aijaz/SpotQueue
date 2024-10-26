from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.user_models import User 
from fastapi import HTTPException
from app.core.config import settings

def create_user(db:Session,name:str,email:str,hashed_password:str):
    """
        Create a new user in the database.

        This function checks if a user with the given email already exists. If not, it hashes
        the provided plaintext password and creates a new user with the provided name, email,
        and hashed password.

        Parameters:
            - db (Session): The database session.
            - name (str): The name of the user.
            - email (str): The email of the user.
            - password (str): The plaintext password of the user.

        Raises:
            - HTTPException: If the email already exists (status code 400).
            - HTTPException: If there is an error creating the user (status code 500).

        Returns:
            - User: The newly created user object.
    """
    try:
        existing_user= get_user_by_email(db,email)
        if existing_user:
            raise HTTPException(status_code=400,detail="Email already exist") 
        new_user = User(name=name,email=email,hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        settings.logger.info(f"User created successfully: {new_user.email}")
        return new_user
    except Exception as e:
        db.rollback()
        settings.logger.error(f"Error on creating user: {e}", exc_info=True)
        raise HTTPException(status_code=500,detail=f"Error on creating user: {e}")

def get_user_by_email(db:Session,email:str):
    """
        Retrieve a user by their email address.

        This function queries the database for a user with the specified email.

        Parameters:
            - db (Session): The database session.
            - email (str): The email of the user to retrieve.

        Raises:
            - HTTPException: If there is an error querying the database (status code 500).

        Returns:
            - User: The user object if found, otherwise None.
    """
    try:    
        query = text("SELECT * FROM users WHERE email = :email")
        result  = db.execute(query,{"email":email})
        user = result.fetchone()    
        if not user:
            settings.logger.info(f"No user found with email: {email}")
        return user
    except Exception as e:
        settings.logger.error(f"Error on get_user_by_email: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error on get_user_by_email: {e}" )

def get_all_users(db:Session):
    """
        Retrieve all users from the database.

        This function fetches all user records stored in the database.

        Parameters:
            - db (Session): The database session.

        Raises:
            - HTTPException: If no users are found (status code 400).
            - HTTPException: If there is an error fetching the users (status code 500).

        Returns:
            - list[User]: A list of user objects.
    """
    try:
        users = db.query(User).all()
        if not users:
            settings.logger.warning("No users found in the database.")
            raise HTTPException(status_code=400,detail="User not found")
        settings.logger.info("Fetched all users from the database.")
        return users
    except Exception as e:
        settings.logger.error(f"Error on fetching users: {e}", exc_info=True)
        raise HTTPException(status_code=500,detail=f"Error on fetching the user {e}")

def get_user_by_username(db:Session,name:str):
    """
        Retrieve a user by their username.

        This function queries the database for a user with the specified username.

        Parameters:
            - db (Session): The database session.
            - name (str): The username of the user to retrieve.

        Raises:
            - HTTPException: If the user is not found (status code 400).
            - HTTPException: If there is an error querying the database (status code 500).

        Returns:
            - User: The user object if found, otherwise None.
    """
    try:
        query=text("SELECT * FROM users WHERE name = :name")
        result = db.execute(query,{"name":name})
        user = result.fetchone()
        if not user:
            settings.logger.warning(f"No user found with username: {name}")
            raise HTTPException(status_code=400,detail="User not found or exist")
        settings.logger.info(f"User retrieved: {name}")
        return user
    except Exception as e:
        settings.logger.error(f"Error on get_user_by_username: {e}", exc_info=True)
        raise HTTPException(status_code=500,detail=f"Error on get_user_by_username: {e}")