# app/models/chat_session.py
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    employee_id = Column(
        String(10), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    session_id = Column(String(10), primary_key=True)
    start_time = Column(DateTime(timezone=True), default=func.now())
    end_time = Column(DateTime(timezone=True))
    summary = Column(Text)
    escalated = Column(Boolean, default=False)
    suggestions = Column(Text)
    risk_score = Column(Integer)

    # Relationships
    employee = relationship("Employee", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )

    def update(self, **kwargs):
        """Update chat session attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
