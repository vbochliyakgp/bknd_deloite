# app/api/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, get_current_active_admin
from app.models.employee import Employee, UserType
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.core.security import get_password_hash
from fastapi import Body

router = APIRouter()


@router.get("/users", response_model=List[EmployeeResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_admin),
):
    """
    Get all system users (HR and Admin)
    """
    users = db.query(Employee).all()
    return users

#test failed
@router.post(
    "/users", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_admin),
):
    """
    Create a new system user (HR or Admin)
    """
    existing_user = db.query(Employee).filter(Employee.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = Employee(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        user_type=user.user_type,
        department=user.department,
        position=user.position,
        profile_image=user.profile_image,
        hashed_password=get_password_hash(user.password),
        wellness_check_status=user.wellness_check_status,
        last_vibe=user.last_vibe,
        immediate_attention=user.immediate_attention,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/users/{user_id}", response_model=EmployeeResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_admin),
):
    """
    Get a specific user by ID
    """
    user = db.query(Employee).filter(Employee.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_admin),
):
    """
    Delete a user
    """
    user = db.query(Employee).filter(Employee.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.id.scalar() == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    db.delete(user)
    db.commit()

    return None


@router.post("/users/{employee_id}/reset-password", response_model=EmployeeResponse)
async def reset_employee_password(
    employee_id: str,
    new_password: str = Body(..., min_length=8),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_admin),
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )
    employee.update(hashed_password = get_password_hash(new_password))
    db.commit()
    db.refresh(employee)

    return employee
