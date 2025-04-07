# app/models/rewards.py
from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Reward(Base):
    __tablename__ = "rewards_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        String(10), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    reward_type = Column(String(50), nullable=False)
    reward_date = Column(Date, nullable=False)
    points = Column(Integer, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="rewards")

    def update(self, **kwargs):
        """Update reward attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
