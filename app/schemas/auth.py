# app/schemas/auth.py
from typing import Optional
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

class UserLogin(BaseModel):
    username: str
    password: str

class EmployeeLogin(BaseModel):
    employee_id: str
    password: str




