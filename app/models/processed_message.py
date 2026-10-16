from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func

from app.db.database import Base


class ProcessedMessage(Base):
    __tablename__ = "processed_messages"

    message_sid = Column(String, primary_key=True)
    status = Column(String, nullable=False, default="processing")
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
