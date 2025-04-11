from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user
from app.schemas.review import ReviewCreate, ReviewOut, BadgeOut
from app.services.review import create_review, get_reviews_for_user, get_user_badge
from app.models.user import User
from app.models.session import Session
router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewOut)
def submit_review(
    review: ReviewCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Check if the session is active
    session = db.query(Session).filter(Session.session_id == review.session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if session.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit review without an active session"
        )

    # Ensure the reviewer is the one submitting the review
    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit a review as yourself."
        )
    
    # If valid, proceed to create the review
    return create_review(db, review)

@router.get("/{user_id}", response_model=List[ReviewOut])
def list_reviews(user_id: str, db: Session = Depends(get_db)):
    return get_reviews_for_user(db, user_id)

@router.get("/badges/{user_id}", response_model=BadgeOut)
def get_badge_for_user(user_id: str, db: Session = Depends(get_db)):
    badge = get_user_badge(db, user_id)
    if badge:
        return badge
    else:
        raise HTTPException(status_code=404, detail="Badge not found")
