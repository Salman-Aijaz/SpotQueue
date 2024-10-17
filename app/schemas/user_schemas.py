from pydantic import BaseModel,Field,EmailStr
from typing import Literal

class UserCreate(BaseModel):
    username:str= Field(...,min_length=3,max_length=50)
    email: EmailStr
    password:str =Field(...,min_length=6)
    role: Literal["User", "Client"] = "User"

class UserIn(BaseModel):
    id:int
    username:str
    role:str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token:str
    token_type:str
