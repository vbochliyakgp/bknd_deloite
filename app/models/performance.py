# app/models/performance.py
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.employee import Employee

class PerformanceData(Base):
    __tablename__ = "performance_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        String(10), ForeignKey(Employee.id, ondelete="CASCADE"), nullable=False
    )
    review_period = Column(Date, nullable=False)
    performance_rating = Column(Integer, nullable=False)
    manager_feedback = Column(Text)
    promotion_consideration = Column(Boolean, nullable=False, default=False)

    # Relationships
    employee = relationship("Employee", back_populates="performance")

    def update(self, **kwargs):
        """Update performance attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
