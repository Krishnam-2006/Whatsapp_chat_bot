from sqlalchemy import Column, String, Integer
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    whatsapp_number = Column(String, primary_key=True)
    state = Column(String, default="IDLE", nullable=False)
    diet_type = Column(String, nullable=True)
    taste_preference = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
