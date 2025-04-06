# app/models/chat_session.py
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.database import Base
import enum


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ESCALATED = "escalated"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    session_status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    start_time = Column(TIMESTAMP(timezone=True), server_default=func.now())
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    summary = Column(Text, nullable=True)
    escalated = Column(Boolean, default=False)  # Renamed from escalated_to_hr
    reason = Column(Text, nullable=True)  # Renamed from escalation_reason
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    employee = relationship("Employee", back_populates="chat_sessions")
    messages = relationship(
        "Message", back_populates="chat_session", cascade="all, delete-orphan"
    )
