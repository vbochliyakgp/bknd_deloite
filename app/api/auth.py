# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.dependencies import get_db
from app.models.employee import Employee
from app.schemas.auth import Token, EmployeeLogin
from app.core.security import verify_password, create_access_token
from app.config import settings

router = APIRouter()


@router.post("/login/user", response_model=Token)
async def login_user(user_login: EmployeeLogin, db: Session = Depends(get_db)):
    """
    Login for HR and Admin users
    """
    user = db.query(Employee).filter(Employee.id == user_login.employee_id).first()

    if not user or not verify_password(user_login.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # if not bool(user.is_active):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Inactive user",
    #     )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/employee", response_model=Token)
async def login_employee(employee_login: EmployeeLogin, db: Session = Depends(get_db)):
    """
    Login for employees
    """
    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_login.employee_id)
        .first()
    )

    if not employee or not verify_password(
        employee_login.password, str(employee.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect employee ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not bool(employee.is_active):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive employee",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=employee.id, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
