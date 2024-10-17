from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.user_models import User 
from fastapi import HTTPException

def create_user(db:Session,name:str,email:str,hashed_password:str):
    """
        Creates a new user in the database.
    
        Args:
            db (Session): The SQLAlchemy database session to perform operations.
            name (str): The username of the new user.
            email (str): The email address of the new user.
            hashed_password (str): The hashed password for the new user.
    
        Returns:
            User: The newly created User object.
    
        Raises:
            HTTPException: If the email already exists in the database or any other 
            error occurs during the operation.
    
        Example:
            create_user(db, "JohnDoe", "john@example.com", "hashed_password_123")
    """
    try:
        existing_user= get_user_by_email(db,email)
        if existing_user:
            raise HTTPException(status_code=400,detail="Email already exist") 
        new_user = User(username=name,email=email,hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Error on creating user: {e}")

def get_user_by_email(db:Session,email:str):
    """
        Retrieves a user by their email address.
    
        Args:
            db (Session): The SQLAlchemy database session to perform operations.
            email (str): The email address of the user to search for.
    
        Returns:
            User: The User object corresponding to the provided email.
    
        Raises:
            HTTPException: If the user is not found or any other error occurs during the query.
    
        Example:
            get_user_by_email(db, "john@example.com")
    """
    try:    
        query = text("SELECT * FROM users WHERE email = :email")
        result  = db.execute(query,{"email":email})
        user = result.fetchone()    
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error on get_user_by_email: {e}" )

def get_all_users(db:Session):
    """
        Retrieves all users from the database.
    
        Args:
            db (Session): The SQLAlchemy database session to perform operations.
    
        Returns:
            list: A list of User objects representing all users in the database.
    
        Raises:
            HTTPException: If no users are found or any other error occurs during the query.
    
        Example:
            get_all_users(db)
    """
    try:
        users = db.query(User).all()
        if not users:
            raise HTTPException(status_code=400,detail="User not found")
        return users
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error on fetching the user {e}")

def get_user_by_username(db:Session,name:str):
    """
        Retrieves a user by their username.
    
        Args:
            db (Session): The SQLAlchemy database session to perform operations.
            name (str): The username of the user to search for.
    
        Returns:
            User: The User object corresponding to the provided username.
    
        Raises:
            HTTPException: If the user is not found or any other error occurs during the query.
    
        Example:
            get_user_by_username(db, "JohnDoe")
    """
    try:
        query=text("SELECT * FROM users WHERE username = :name")
        result = db.execute(query,{"name":name})
        user = result.fetchone()
        if not user:
            raise HTTPException(status_code=400,detail="User not found or exist")
        return user
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error on get_user_by_username: {e}")