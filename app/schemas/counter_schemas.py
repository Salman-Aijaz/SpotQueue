from pydantic import BaseModel


class CounterCreate(BaseModel):
    counter_number: int
    service_name: str

class CounterResponse(BaseModel):
    id: int
    counter_number: int
    service_id: int

    class Config:
        orm_mode = True

class NextPersonRequest(BaseModel):
    user_id: int
