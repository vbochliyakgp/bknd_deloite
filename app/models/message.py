# app/models/message.py
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.database import Base
import enum

class MessageSender(str, enum.Enum):
    BOT = "bot"
    EMPLOYEE = "employee"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    sender = Column(Enum(MessageSender))
    content = Column(Text)
    sentiment = Column(Float, nullable=True)  # Added field
    feedback = Column(Boolean, nullable=True)  # Added field
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")