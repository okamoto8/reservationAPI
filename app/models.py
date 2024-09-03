from sqlalchemy import Column,Integer,String,DateTime
from .database import Base

class Reservation(Base):
    __tablename__ = 'reservation'
    
    userId = Column(Integer,primary_key=True,index=True,nullable=False ,autoincrement=True)
    userName = Column(String,unique=False,index=True,nullable=False)
    startTime =Column(DateTime,unique=False,index=True,nullable=False)
    endTime = Column(DateTime,unique=False,index=True,nullable=False)