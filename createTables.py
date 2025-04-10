from app.database import Base, engine
from app.models import user  # Important: import your models first

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("All tables created!")
