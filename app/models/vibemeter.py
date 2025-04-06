# app/models/vibemeter.py
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP, DATE
from app.database import Base
import enum

class EmotionZone(str, enum.Enum):
    FRUSTRATED = "Frustrated"
    SAD = "Sad"
    OKAY = "Okay"
    HAPPY = "Happy"
    EXCITED = "Excited"

class VibemeterResponse(Base):
    __tablename__ = "vibe_responses"  # Renamed from vibemeter_responses

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(DATE, default=func.current_date())  # Renamed from response_date
    score = Column(Float)  # Added field
    vibe_zone = Column(Enum(EmotionZone))  # Renamed from emotion_zone
    feedback = Column(Text, nullable=True)  # Renamed from comment
    sentiment = Column(Float, nullable=True)  # Added field
    trigger_flag = Column(Boolean, nullable=True)  # Added field
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="vibe_responses")  # Updated relationship name