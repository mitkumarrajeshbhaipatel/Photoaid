from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.user import UserCreate, UserOut
from app.services.auth import create_user, get_user_by_email, get_user_by_id, get_all_users , reset_password_request, change_password
from app.utils.security import verify_password, create_access_token

from app.services.profile import create_user_profile  # import profile service
from app.schemas.profile import UserProfileCreate     # import profile schema
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Register a new user
@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Create the user
    new_user = create_user(db, user)

    # Automatically create a blank profile for the new user
    profile_data = UserProfileCreate(
        user_id=new_user.id,
        name=new_user.name,
        bio="",
        is_available=False,
        avatar_url="",
        country=""
    )
    create_user_profile(db, profile_data)

    return new_user

# Login (simple email and password check)
@router.post("/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email)
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.id})
    return {"access_token": access_token, "token_type": "bearer", "user": UserOut.from_orm(db_user)}
# Get user by ID
@router.get("/user/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

# List all users
@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return get_all_users(db)

# Forget Password: Generate a temporary reset token
@router.post("/forget-password")
def forget_password(email: str, db: Session = Depends(get_db)):
    token = reset_password_request(db, email)
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "Password reset token generated successfully", "reset_token": token}

# Change Password: Use reset token to set a new password
@router.post("/change-password")
def reset_user_password(token: str, new_password: str, db: Session = Depends(get_db)):
    success = change_password(db, token, new_password)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    return {"message": "Password changed successfully"}