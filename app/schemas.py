import datetime
from pydantic import BaseModel,Field

class ReservationCreate(BaseModel):
    userName:str
    startTime:datetime.datetime
    endTime:datetime.datetime
    resourceId:int

class Reservation(ReservationCreate):
    userId:int
    
    class Config:
        orm_mode = True


class ResourceCreate(BaseModel):
    resourceName:str
    
    class Config:
        orm_mode =True

class Resource(ResourceCreate):
    resourceId:int
    
    class config:
        orm_mode =True

class ResourceUpdate(BaseModel):
    resourceName: str

    class Config:
        orm_mode = True