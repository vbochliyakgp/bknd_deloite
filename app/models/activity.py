# app/models/activity.py
from sqlalchemy import Column, Integer, ForeignKey, Float, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date, default=func.current_date())
    hours_worked = Column(Float)
    meetings_attended = Column(Integer)
    emails_sent = Column(Integer)
    after_hours_work = Column(Float)  # Work done outside standard hours
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="activity_records")