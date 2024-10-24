from pydantic import BaseModel

class TokenRequest(BaseModel):
    email: str
    service_name: str
    latitude: float
    longitude: float

class TokenCreate(BaseModel):
    user_id: int
    service_id: int
    counter_id: int
    latitude: float
    longitude: float

class TokenResponse(BaseModel):
    token_number: int  # Ensure this is updated to match the new type
    user_id: int
    service_id: int
    counter_id: int
    distance: float  # Ensure this is set to float
    duration: int
    status: str
    work_status: str
    
    class Config:
        orm_mode = True

class UpdateTokenRequest(BaseModel):
    user_id:int
    latitude:float
    longitude:float