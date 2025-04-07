# app/models/message.py
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Message(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        String(10),
        ForeignKey("chat_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def update(self, **kwargs):
        """Update chat message attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
