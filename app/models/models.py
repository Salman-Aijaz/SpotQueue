from sqlalchemy import Column,Integer
from sqlalchemy.orm import relationship
from app.db.database import Base

class Counter(Base):
    __tablename__ = "counters"
    id = Column(Integer,primary_key=True,index=True)
    counter = Column(Integer,nullable=False,unique=True)