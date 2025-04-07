from sqlalchemy import (
    Column,
    String,
    Boolean,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserType(enum.Enum):
    admin = "admin"
    hr = "hr"
    employee = "employee"


class WellnessCheckStatus(enum.Enum):
    not_received = "not_received"
    not_started = "not_started"
    completed = "completed"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(10), nullable=False)
    department = Column(String(50))
    position = Column(String(100))
    user_type = Column(Enum(UserType), nullable=False)
    profile_image = Column(String(255))
    wellness_check_status = Column(
        Enum(WellnessCheckStatus),
        nullable=False,
        default=WellnessCheckStatus.not_received,
    )
    last_vibe = Column(String(20), nullable=False)
    immediate_attention = Column(Boolean, nullable=False)

    def update(self, **kwargs):
        """Update employee attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
