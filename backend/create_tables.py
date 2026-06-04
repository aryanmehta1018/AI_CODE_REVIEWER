from app.db.database import Base, engine

# Import models here
from app.models.user import User
from app.models.review import Review

Base.metadata.create_all(bind=engine)

print("Tables created successfully")