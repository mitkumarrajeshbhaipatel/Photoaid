from app.models.user import User
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash, create_reset_token, verify_reset_token
import datetime, uuid

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

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

# Generate reset token
def reset_password_request(db: Session, email: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    reset_token = create_reset_token(user.id)
    return reset_token

# Change password using reset token
def change_password(db: Session, token: str, new_password: str):
    user_id = verify_reset_token(token)
    if not user_id:
        return False
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(user)
    return True
