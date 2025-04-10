from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.schemas.review import ReviewCreate, ReviewOut
from app.services.review import create_review, get_reviews_for_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewOut)
def submit_review(review: ReviewCreate, db: Session = Depends(get_db)):
    return create_review(db, review)

@router.get("/{user_id}", response_model=List[ReviewOut])
def list_reviews(user_id: str, db: Session = Depends(get_db)):
    return get_reviews_for_user(db, user_id)
