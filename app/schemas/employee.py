
# app/schemas/employee.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class EmployeeBase(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    department: str
    position: str
    manager_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    password: str

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None

class EmployeeInDBBase(EmployeeBase):
    id: int
    is_active: bool
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
