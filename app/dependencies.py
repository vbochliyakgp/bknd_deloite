# app/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import (
    get_current_user,
    get_current_active_admin,
    get_current_active_hr,
    get_current_employee,
)
from app.models.employee import Employee

# Re-export dependencies
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_admin",
    "get_current_active_hr",
    "get_current_employee",
]
