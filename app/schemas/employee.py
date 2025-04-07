from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum


class UserType(str, Enum):
    admin = "admin"
    hr = "hr"
    employee = "employee"


class WellnessCheckStatus(str, Enum):
    not_recieved = "not_recieved"
    not_started = "not_started"
    completed = "completed"


class EmployeeBase(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str
    user_type: UserType
    department: Optional[str] = None
    position: Optional[str] = None
    profile_image: Optional[str] = None
    wellness_check_status: WellnessCheckStatus
    last_vibe: str
    immediate_attention: bool


class EmployeeCreate(EmployeeBase):
    password: str


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    user_type: Optional[UserType] = None
    department: Optional[str] = None
    position: Optional[str] = None
    profile_image: Optional[str] = None
    wellness_check_status: Optional[WellnessCheckStatus] = None
    last_vibe: Optional[str] = None
    immediate_attention: Optional[bool] = None


class EmployeeInDBBase(EmployeeBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EmployeeResponse(EmployeeInDBBase):
    pass


class EmployeeWithAnalytics(EmployeeResponse):
    recent_vibe: Optional[str] = None
    leave_balance: Optional[int] = None
    average_hours_worked: Optional[float] = None
    latest_performance_rating: Optional[float] = None
    rewards_count: Optional[int] = None
