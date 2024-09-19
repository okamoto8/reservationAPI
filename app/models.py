from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from .database import Base

class Reservation(Base):
    __tablename__ = 'reservation'
    
    userId = Column(Integer,primary_key=True,index=True,nullable=False ,autoincrement=True)
    userName = Column(String,unique=False,index=True,nullable=False)
    startTime =Column(DateTime,unique=False,index=True,nullable=False)
    endTime = Column(DateTime,unique=False,index=True,nullable=False)
    resourceId = Column(Integer,ForeignKey('resources.resourceId',ondelete='SET NULL'),nullable=False)

class Resources(Base):
    __tablename__='resources'
    
    resourceId = Column(Integer,primary_key=True,index=True,nullable=False,autoincrement=True)
    resourceName = Column(String,unique=True,index=True,nullable=False)

