from app.models.token_models import Token
from app.schemas.token_schemas import TokenCreate
from sqlalchemy.orm import Session
from sqlalchemy import func

def create_token_record(db: Session, token_data: TokenCreate):
    # Generate a unique token number based on the maximum existing token_number
    max_token_number = db.query(func.max(Token.token_number)).scalar() or 0
    new_token = Token(
        token_number=max_token_number + 1,  # Increment the max token number
        user_id=token_data.user_id,
        service_id=token_data.service_id,
        counter_id=token_data.counter_id,
        latitude=token_data.latitude,
        longitude=token_data.longitude,
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return new_token
