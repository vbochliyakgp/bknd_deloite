# app/models/employee.py
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True)  # Company ID (e.g., DEL123)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)  # Added field
    department = Column(String)
    position = Column(String)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    join_date = Column(Date)  # Added field
    profile_image = Column(String, nullable=True)  # Added field
    status = Column(String)  # Added field
    last_vibe = Column(String, nullable=True)  # Added field 
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    manager = relationship("Employee", remote_side=[id], backref="team_members")
    vibe_responses = relationship("VibemeterResponse", back_populates="employee")  # Renamed from vibemeter_responses
    leave_records = relationship("Leave", back_populates="employee")
    activity_records = relationship("Activity", back_populates="employee")
    performance_records = relationship("Performance", back_populates="employee")
    reward_records = relationship("Reward", back_populates="employee")
    chat_sessions = relationship("ChatSession", back_populates="employee")