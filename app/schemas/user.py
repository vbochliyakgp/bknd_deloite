# app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.employee import UserType


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserType


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserType] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserResponse(UserInDBBase):
    pass
