from datetime import time
from pydantic import BaseModel

# SCHEMAS FOR CREATING A SERVICES
class ServiceCreate(BaseModel):
    service_name:str
    service_entry_time:time
    service_end_time:time
    number_of_counters: int


# SCHEMAS FOR RETURNING A SERVICE
class ServiceResponse(BaseModel):
    id:int
    service_name:str
    service_entry_time:time
    service_end_time:time
    number_of_counters: int

    class Config:
        orm_mode = True