from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash
from sqlalchemy.orm import Session
import uuid
import datetime

def create_user(db: Session, user: UserCreate):
    db_user = User(
        id=str(uuid.uuid4()),
        name=user.name,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        is_verified=False,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
