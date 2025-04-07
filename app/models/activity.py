# app/models/activity.py
from sqlalchemy import Column, Integer, ForeignKey, String, Date
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.employee import Employee

class Activity(Base):
    __tablename__ = "activity_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        String(10), ForeignKey(Employee.id, ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False)
    hours_worked = Column(Integer, nullable=False)
    meetings_attended = Column(Integer, nullable=False)
    emails_sent = Column(Integer, nullable=False)
    teams_messages_sent = Column(Integer, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="activity_data")

    def update(self, **kwargs):
        """Update activity attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
