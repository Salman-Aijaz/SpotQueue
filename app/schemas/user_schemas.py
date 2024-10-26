from pydantic import BaseModel,Field,EmailStr
from typing import Literal
from enum import Enum
class UserRole(str,Enum):
    USER="User"
    CLIENT="Client"
class UserCreate(BaseModel):
    name:str= Field(...,min_length=3,max_length=50)
    email: EmailStr
    password:str =Field(...,min_length=6)
    role: UserRole=UserRole.USER

class UserIn(BaseModel):
    id:int
    name:str
    email: str
    role:UserRole

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token:str
    token_type:str
