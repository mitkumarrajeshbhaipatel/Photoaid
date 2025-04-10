from sqlalchemy.orm import Session
from app.models.review import Review, Badge
from app.schemas.review import ReviewCreate
import uuid
import datetime

def create_review(db: Session, review: ReviewCreate):
    db_review = Review(
        review_id=str(uuid.uuid4()),
        session_id=review.session_id,
        reviewer_id=review.reviewer_id,
        target_user_id=review.target_user_id,
        rating=review.rating,
        comment=review.comment,
        submitted_at=datetime.datetime.utcnow()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    # Auto-assign badges based on rating
    if review.rating == 5:
        assign_badge(db, review.target_user_id, "5-Star Rated")

    return db_review

def assign_badge(db: Session, user_id: str, badge_type: str):
    badge = Badge(
        user_id=user_id,
        badge_type=badge_type,
        awarded_at=datetime.datetime.utcnow()
    )
    db.add(badge)
    db.commit()
    db.refresh(badge)
    return badge

def get_reviews_for_user(db: Session, user_id: str):
    return db.query(Review).filter(Review.target_user_id == user_id).all()
