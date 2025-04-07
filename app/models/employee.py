from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Text,
    Date,
    ForeignKey,
    DateTime,
    Enum,
    CheckConstraint,
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
    not_recieved = "not_recieved"
    not_started = "not_started"
    completed = "completed"


class Employee(Base):
    __tablename__ = "employeess"

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
        default=WellnessCheckStatus.not_recieved,
    )
    last_vibe = Column(String(20), nullable=False)
    immediate_attention = Column(Boolean, nullable=False)

    # Relationships
    chat_sessions = relationship(
        "ChatSession", back_populates="employee", cascade="all, delete-orphan"
    )
    activity_data = relationship(
        "ActivityData", back_populates="employee", cascade="all, delete-orphan"
    )
    leaves = relationship(
        "LeaveData", back_populates="employee", cascade="all, delete-orphan"
    )
    onboarding = relationship(
        "OnboardingData", back_populates="employee", cascade="all, delete-orphan"
    )
    rewards = relationship(
        "RewardData", back_populates="employee", cascade="all, delete-orphan"
    )
    performance = relationship(
        "PerformanceData", back_populates="employee", cascade="all, delete-orphan"
    )
    vibemeter = relationship(
        "VibemeterData", back_populates="employee", cascade="all, delete-orphan"
    )

    def update(self, **kwargs):
        """Update employee attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
