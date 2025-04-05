
# app/models/rewards.py
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.database import Base

class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    reward_type = Column(String)  # e.g., "Spot Bonus", "Employee of the Month"
    reward_date = Column(Date)
    amount = Column(Integer, nullable=True)  # If applicable (e.g., bonus amount)
    description = Column(Text)
    awarded_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="reward_records")
    awarded_by_employee = relationship("Employee", foreign_keys=[awarded_by])

