from sqlalchemy import Column, String

from app.db.database import Base


class ProcessedMessage(Base):
    __tablename__ = "processed_messages"

    message_sid = Column(String, primary_key=True)
    status = Column(String, nullable=False, default="processing")
