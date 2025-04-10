from app.database import Base, engine
from app.models import user, profile, report, location, matchmaking, session, chat, notification, review

print("Creating database tables...")

# Create all tables from imported models
Base.metadata.create_all(bind=engine)

print("All tables created successfully!")
