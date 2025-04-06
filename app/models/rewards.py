# app/models/rewards.py
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.database import Base

class Reward(Base):
    __tablename__ = "rewards_data"  # Renamed from rewards

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    reward_type = Column(String)  # e.g., "Spot Bonus", "Employee of the Month"
    reward_date = Column(Date)
    days_count = Column(Integer, nullable=True)  # Added field
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="reward_records")