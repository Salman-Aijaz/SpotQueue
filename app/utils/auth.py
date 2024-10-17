from passlib.context import CryptContext
from jose import jwt
from datetime import datetime,timedelta
from app.core.config import settings
from fastapi import HTTPException
from app.core.config import settings

# Password encryption context using bcrypt algorithm
pwd_context= CryptContext(schemes=["bcrypt"],deprecated="auto")

def get_password_hash(password:str):
    """
        Hashes the provided plain-text password using bcrypt.

        Args:
            password (str): The plain-text password to be hashed.

        Returns:
            str: The hashed password.

        Raises:
            HTTPException: Raises an internal server error (500) if password hashing fails.
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        settings.logger.error("Error hashing password: %s",e)
        raise HTTPException(status_code=500,detail=f"Internal Server Error: Error hashing password. {e}")

def verify_password(plain_password,hashed_password):
    """
        Verifies that a provided plain-text password matches a stored hashed password.

        Args:
            plain_password (str): The plain-text password provided by the user.
            hashed_password (str): The hashed password stored in the system.

        Returns:
            bool: True if the plain-text password matches the hashed password, False otherwise.

        Raises:
            HTTPException: Raises an internal server error (500) if password verification fails.
    """
    try:
        return pwd_context.verify(plain_password,hashed_password)
    except Exception as e:
        settings.logger.error("Error verifying password: %s", e)
        raise HTTPException(status_code=500,detail=f"Internal Server Error: Error verifying password. {e}")

def create_access_token(data:dict,expires_delta:timedelta|None =None):
    """
        Creates a JWT access token with an optional expiration time.

        Args:
            data (dict): The payload data to encode within the token.
            expires_delta (timedelta | None, optional): Time duration until the token expires.
                If not provided, the token expires after a default time as defined in settings.

        Returns:
            str: The encoded JWT token as a string.

        Raises:
            HTTPException: Raises an internal server error (500) if access token creation fails.
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(settings.UTC)+expires_delta
        else:
            expire= datetime.now(settings.UTC)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp":expire})
        encode_jwt= jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
        return encode_jwt        
    except Exception as e:
        settings.logger.error("Error creating access token %s",e)
        raise HTTPException(status_code=500,detail=f"Internal Server Error: Error creating_access_token. {e}")
