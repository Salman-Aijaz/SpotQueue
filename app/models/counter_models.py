from app.db.database import Base
from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship

class Counter(Base):
    __tablename__="counters"

    id = Column(Integer,primary_key=True,index=True)
    counter_number= Column(Integer,nullable=False)
    service_id=Column(Integer,ForeignKey("services.id"),nullable=False)

    service=relationship("Service",back_populates="counters")
    tokens = relationship("Token", back_populates="counter")