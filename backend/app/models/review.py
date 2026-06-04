from sqlalchemy import Column, Integer, Text, ForeignKey
from app.db.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(Text)

    review = Column(Text)

    user_id = Column(Integer, ForeignKey("users.id"))