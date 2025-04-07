# app/schemas/employee.py

from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum


class EmployeeRole(str, Enum):
    ADMIN = "0"
    HR = "1"
    EMPLOYEE = "2"


class WellnessCheckStatus(str, Enum):
    not_received = "0"
    not_started = "1"
    completed = "2"


class EmployeeBase(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: EmployeeRole
    department: str
    position: str
    profile_image: Optional[str] = None
    wellness_check_status: WellnessCheckStatus
    last_vibe: Optional[str] = None
    immediate_action: bool


class EmployeeCreate(EmployeeBase):
    password: str


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[EmployeeRole] = None
    department: Optional[str] = None
    position: Optional[str] = None
    profile_image: Optional[str] = None
    wellness_check_status: Optional[WellnessCheckStatus] = None
    last_vibe: Optional[str] = None
    immediate_action: Optional[bool] = None


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
