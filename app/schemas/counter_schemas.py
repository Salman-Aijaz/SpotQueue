from pydantic import BaseModel
from typing import Optional


class CounterCreate(BaseModel):
    counter_number: int
    service_name: str
    user_id: Optional[int] = None  # User can be None if not occupied

class CounterResponse(BaseModel):
    id: int
    counter_number: int
    service_id: int
    user_id: Optional[int]

    class Config:
        orm_mode = True