from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Onboarding(Base):
    __tablename__ = "onboarding_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        String(10), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    onboarding_feedback = Column(String(50))
    joining_date = Column(Date, nullable=False)
    mentor_assigned = Column(Boolean, nullable=False, default=False)
    training_completed = Column(Boolean, nullable=False, default=False)

    # Relationships
    employee = relationship("Employee", back_populates="onboarding")

    def update(self, **kwargs):
        """Update onboarding attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
