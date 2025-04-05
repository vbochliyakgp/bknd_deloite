
# app/models/vibemeter.py
from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Text
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
    __tablename__ = "vibemeter_responses"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    response_date = Column(DATE, default=func.current_date())
    emotion_zone = Column(Enum(EmotionZone))
    comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="vibemeter_responses")

