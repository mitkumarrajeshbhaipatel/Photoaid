from app.database import Base, engine
from app.models import user, profile, verification, report, location, match, session, chat, notification, review, badge

print("Creating database tables...")

# Create all tables from imported models
Base.metadata.create_all(bind=engine)

print("All tables created successfully!")
