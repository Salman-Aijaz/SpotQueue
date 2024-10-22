from sqlalchemy import Boolean, Column, Float, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base 

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_number = Column(Integer, unique=True, index=True)  # Unique token number
    queue_position = Column(Integer)  # Position of the token in the queue
    issue_time = Column(DateTime, default=datetime.now(timezone.utc))  # Timestamp of token issuance


    latitude = Column(Float, nullable=False)  # Latitude of the user
    longitude = Column(Float, nullable=False)  # Longitude of the user
    
    distance = Column(Float,nullable=True)
    duration = Column(Integer,nullable=True)

    reach_out = Column(Boolean, default=False)  # Default to False

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Link to the User table
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)  # Link to the Service table
    counter_id = Column(Integer, ForeignKey("counters.id"), nullable=False)  # Link to the Counter table

    # Relationships
    user = relationship("User", back_populates="tokens")  # Establish relationship with User
    service = relationship("Service", back_populates="tokens")  # Establish relationship with Service
    counter = relationship("Counter", back_populates="tokens")  # Establish relationship with Counter