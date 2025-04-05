

# app/models/performance.py
from sqlalchemy import Column, String, Integer, ForeignKey, Float, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from app.database import Base

class Performance(Base):
    __tablename__ = "performances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    review_period = Column(String)  # e.g., "2023 Q1", "2023 Annual"
    rating = Column(Float)  # e.g., 1-5 scale
    review_date = Column(Date)
    reviewer_id = Column(Integer, ForeignKey("employees.id"))
    promotion_eligible = Column(Boolean, default=False)
    strengths = Column(Text, nullable=True)
    areas_for_improvement = Column(Text, nullable=True)
    comments = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="performance_records")
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])

