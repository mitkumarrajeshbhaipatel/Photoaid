from sqlalchemy.orm import Session
from app.models.review import Review, Badge
from app.models.profile import UserProfile
from app.schemas.review import ReviewCreate
import uuid
import datetime


def create_review(db: Session, review: ReviewCreate):

    existing_review = db.query(Review).filter(
        Review.session_id == review.session_id,
        Review.reviewer_id == review.reviewer_id
    ).first()

    if existing_review:
        raise ValueError("User has already submitted a review for this session.")
        
    # Create the review
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

    # Assign a badge and update profile
    badge = assign_badge(db, review.target_user_id)

    # Update user's profile stats
    profile = db.query(UserProfile).filter(UserProfile.user_id == review.target_user_id).first()
    if profile:
        reviews = db.query(Review).filter(Review.target_user_id == review.target_user_id).all()
        total_reviews = len(reviews)
        average_rating = sum([r.rating for r in reviews]) / total_reviews if total_reviews > 0 else 0.0

        profile.total_sessions = total_reviews
        profile.average_rating = average_rating

        # Add badge to trust_badges if not already included
        if badge and badge.badge_type not in profile.trust_badges:
            profile.trust_badges.append(badge.badge_type)

        db.commit()
        db.refresh(profile)

    return db_review


def assign_badge(db: Session, user_id: str):
    reviews = db.query(Review).filter(Review.target_user_id == user_id).all()

    if not reviews:
        return None

    total_reviews = len(reviews)
    average_rating = sum([r.rating for r in reviews]) / total_reviews

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

    existing_badge = db.query(Badge).filter(Badge.user_id == user_id).first()

    if existing_badge:
        if existing_badge.badge_type != badge_type:
            existing_badge.badge_type = badge_type
            existing_badge.awarded_at = datetime.datetime.utcnow()
            db.commit()
            db.refresh(existing_badge)
        return existing_badge

    new_badge = Badge(
        user_id=user_id,
        badge_type=badge_type,
        awarded_at=datetime.datetime.utcnow()
    )
    db.add(new_badge)
    db.commit()
    db.refresh(new_badge)

    return new_badge


def get_user_badge(db: Session, user_id: str):
    return db.query(Badge).filter(Badge.user_id == user_id).first()


def get_reviews_for_user(db: Session, user_id: str):
    return db.query(Review).filter(Review.target_user_id == user_id).all()
