from sqlalchemy import Column, String

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    whatsapp_number = Column(String, primary_key=True)
    state = Column(String, default="IDLE", nullable=False)
    diet_type = Column(String, nullable=True)
    taste_preference = Column(String, nullable=True)
