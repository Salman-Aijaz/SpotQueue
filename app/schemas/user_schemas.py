from pydantic import BaseModel,Field,EmailStr
from typing import Literal

class UserCreate(BaseModel):
    """
        Schema for creating a new user.

        This schema is used to validate the input data when registering a new user.
        It includes the user's name, email, password, and role.

        Attributes:
            name (str): The name of the user (must be between 3 and 50 characters).
            email (EmailStr): The email address of the user (must be a valid email format).
            password (str): The user's password (must be at least 6 characters long).
            role (Literal["User", "Client"]): The role of the user, default is "User".
    """
    name:str= Field(...,min_length=3,max_length=50)
    email: EmailStr
    password:str =Field(...,min_length=6)
    role: Literal["User", "Client"] = "User"

class UserIn(BaseModel):
    """
        Schema for representing a user in API responses.

        This schema is used to serialize user data when retrieving user information.
        It includes the user's ID, name, and role.

        Attributes:
            id (int): The unique identifier for the user.
            name (str): The name of the user.
            role (str): The role of the user.
    """
    id:int
    name:str
    email: str
    role:str

    class Config:
        """
            Configuration options for the UserIn schema.
        
            Enables compatibility with ORM models, allowing Pydantic to 
            read data from SQLAlchemy models directly.
        """
        orm_mode = True

class Token(BaseModel):
    """
        Schema for representing an access token.

        This schema is used to return access token information upon successful login.
        It includes the token itself and the type of token.

        Attributes:
            access_token (str): The JWT access token.
            token_type (str): The type of token (usually "bearer").
    """
    access_token:str
    token_type:str
