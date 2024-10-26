from sqlalchemy import Column,Integer,String
from app.db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__="users"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,unique=True,index=True)
    hashed_password=Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="User")

    tokens = relationship("Token", back_populates="user") 