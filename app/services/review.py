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

    assign_badge(db, review.target_user_id)

    return db_review

from sqlalchemy.orm import Session as DBSession
from app.models.review import Review, Badge
import datetime

def assign_badge(db: DBSession, user_id: str):
    # Fetch all reviews for the target user
    reviews = db.query(Review).filter(Review.target_user_id == user_id).all()

    if not reviews:
        return None  # No reviews, no badge assignment

    # Calculate the average rating from all reviews
    total_rating = sum([review.rating for review in reviews])
    average_rating = total_rating / len(reviews)

    # Count the total number of reviews
    total_reviews = len(reviews)

    # Determine the badge based on the average rating and review count
    badge_type = None
    if total_reviews >= 15 and average_rating == 5:
        badge_type = "Platinum Reviewer"
    elif total_reviews >= 10 and average_rating >= 4.5:
        badge_type = "Gold Reviewer"
    elif total_reviews >= 6 and average_rating >= 4.0:
        badge_type = "Silver Reviewer"
    elif total_reviews >= 3 and average_rating >= 3.0:
        badge_type = "Bronze Reviewer"
    elif total_reviews >= 1:
        badge_type = "Newbie"

    # Check if the user already has a badge of this type
    existing_badge = db.query(Badge).filter(Badge.user_id == user_id).first()

    if existing_badge:
        # If the badge type is different, update the badge
        if existing_badge.badge_type != badge_type:
            # Update the existing badge to reflect the new type
            existing_badge.badge_type = badge_type
            existing_badge.awarded_at = datetime.datetime.utcnow()  # Refresh the award date
            db.commit()
            db.refresh(existing_badge)
            return existing_badge
        else:
            # If the badge type is the same, no changes are made
            return existing_badge

    # If the user does not have a badge, assign the new badge
    badge = Badge(
        user_id=user_id,
        badge_type=badge_type,
        awarded_at=datetime.datetime.utcnow()
    )
    db.add(badge)
    db.commit()
    db.refresh(badge)

    return badge




def get_user_badge(db: Session, user_id: str):
    badge = db.query(Badge).filter(Badge.user_id == user_id).first()
    return badge

def get_reviews_for_user(db: Session, user_id: str):
    return db.query(Review).filter(Review.target_user_id == user_id).all()
