import datetime
from pydantic import BaseModel,Field

class ReservationCreate(BaseModel):
    userName:str
    startTime:datetime.datetime
    endTime:datetime.datetime

class Reservation(ReservationCreate):
    userId:int
    
    class Config:
        orm_mode = True