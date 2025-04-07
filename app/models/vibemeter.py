# app/models/vibemeter.py
from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint, Date
from sqlalchemy.orm import relationship
from app.database import Base


class VibemeterData(Base):
    __tablename__ = "vibemeter_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        String(10), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False)
    vibe_score = Column(Integer, nullable=False)
    emotion_zone = Column(String(50), nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="vibemeter")

    # Ensure vibe_score is within a reasonable range (e.g., 1-10)
    __table_args__ = (
        CheckConstraint(
            "vibe_score >= 1 AND vibe_score <= 10", name="check_vibe_score_range"
        ),
    )

    def update(self, **kwargs):
        """Update vibemeter attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
