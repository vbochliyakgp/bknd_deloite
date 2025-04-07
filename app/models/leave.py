# app/models/leave.py
from sqlalchemy import Column, String, Integer, ForeignKey, Date, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Leave(Base):
    __tablename__ = "leaves_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        String(10), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    leave_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    leave_days = Column(Integer, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="leaves")

    # Ensure end_date is not before start_date
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="check_dates_valid"),
    )

    def update(self, **kwargs):
        """Update leave attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
