from sqlalchemy import Column,Integer,String
from app.db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    """
        User model representing the users table in the database.

        This class defines the structure of the User table, including the fields
        that will be stored in the database. It inherits from the Base class
        provided by SQLAlchemy, which includes common functionality for ORM models.
    """
    __tablename__="users"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,unique=True,index=True)
    hashed_password=Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="User")

    counters = relationship("Counter", back_populates="user")
    tokens = relationship("Token", back_populates="user") 