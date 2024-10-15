from pydantic import BaseModel

# SCHEMAS FOR CREATING A NEW COUNTER
class CounterCreate(BaseModel):
    counter:int

# SCHEMAS FOR RETURNING A COUNTER 
class CounterResponse(BaseModel):
    id:int
    counter:int

    class Config:
        orm_mode = True
