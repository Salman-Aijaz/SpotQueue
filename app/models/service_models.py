from sqlalchemy import Column,Integer,String,Time
from sqlalchemy.orm import relationship
from app.db.database import Base


class Service(Base):
    __tablename__="services"

    id = Column(Integer,primary_key=True,index=True)
    service_name= Column(String,nullable=False)
    service_entry_time = Column(Time,nullable=False)
    service_end_time = Column(Time,nullable=False)

    counters = relationship("Counter", back_populates="service")
    tokens = relationship("Token", back_populates="service")