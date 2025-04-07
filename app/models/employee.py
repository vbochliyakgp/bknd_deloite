# app/models/employee.py
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text, Date,Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.database import Base
import enum



class EmployeeRole(str, enum.Enum):
    ADMIN = 0
    HR = 1
    EMPLOYEE = 2

class WellnessCheckStatus(enum.Enum):
    not_received = 0
    not_started = 1
    completed = 2


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone = Column(String)  # Added field
    role =  Column(Enum(EmployeeRole), nullable=False)
    department = Column(String)
    position = Column(String)
    profile_image = Column(String, nullable=True)  # Added field
    wellness_check_status = Column(Enum(WellnessCheckStatus), nullable=False)
    last_vibe = Column(String)
    immediate_action = Column(Boolean)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    vibe_responses = relationship(
        "VibemeterResponse", back_populates="employee"
    )  # Renamed from vibemeter_responses
    leave_records = relationship("Leave", back_populates="employee")
    activity_records = relationship("Activity", back_populates="employee")
    performance_records = relationship("Performance", back_populates="employee")
    reward_records = relationship("Reward", back_populates="employee")
    chat_sessions = relationship("ChatSession", back_populates="employee")

    def update(self, **kwargs):
        """Update user attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
