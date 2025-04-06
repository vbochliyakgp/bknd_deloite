# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.dependencies import get_db
from app.models.user import User
from app.models.employee import Employee
from app.schemas.auth import Token, UserLogin, EmployeeLogin
from app.core.security import verify_password, create_access_token
from app.config import settings
from app.core.auth import get_current_user

router = APIRouter()


@router.post("/login/user", response_model=Token)
async def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Login for HR and Admin users
    """
    user = db.query(User).filter(User.username == user_login.username).first()

    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

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
        employee_login.password, employee.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect employee ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive employee",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=employee.id, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# OAuth2 compatible token login - can be used by third-party integrations
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, for third-party integrations
    """
    # First try to authenticate as a user (HR/Admin)
    user = db.query(User).filter(User.username == form_data.username).first()
    if user and verify_password(form_data.password, user.hashed_password):
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    # Try to authenticate as an employee
    employee = (
        db.query(Employee).filter(Employee.employee_id == form_data.username).first()
    )
    if employee and verify_password(form_data.password, employee.hashed_password):
        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive employee",
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=employee.id, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    # If neither authentication method worked, return error
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change password for authenticated user
    """
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    current_user.hashed_password = get_password_hash(new_password)
    db.commit()

    return {"status": "success", "message": "Password changed successfully"}
