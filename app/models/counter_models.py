from app.db.database import Base
from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship

class Counter(Base):
    __tablename__="counters"

    id = Column(Integer,primary_key=True,index=True)
    counter_number= Column(Integer,nullable=False)
    service_id=Column(Integer,ForeignKey("services.id"),nullable=False)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=True)  # Can be null if not occupied

    service=relationship("Service",back_populates="counters")
    user = relationship("User",back_populates="counters")
    tokens = relationship("Token", back_populates="counter")

