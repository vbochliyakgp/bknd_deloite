# app/api/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db, get_current_active_admin
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.core.security import get_password_hash

router = APIRouter()


# User management (HR and Admin users)
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Get all system users (HR and Admin)
    """
    users = db.query(User).all()
    return users


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Create a new system user (HR or Admin)
    """
    # Check if username or email already exists
    existing_user = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=user.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Get a specific user by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Update a user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update user fields
    if user_update.username is not None:
        # Check if username is being changed and if it's already in use
        if (
            user_update.username != user.username
            and db.query(User).filter(User.username == user_update.username).first()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use",
            )
        user.username = user_update.username

    if user_update.email is not None:
        # Check if email is being changed and if it's already in use
        if (
            user_update.email != user.email
            and db.query(User).filter(User.email == user_update.email).first()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use"
            )
        user.email = user_update.email

    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)

    if user_update.role is not None:
        user.role = user_update.role

    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Delete a user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    db.delete(user)
    db.commit()

    return None


# Employee management
@router.get("/employees", response_model=List[EmployeeResponse])
async def get_all_employees(
    department: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Get all employees
    """
    query = db.query(Employee)

    if active_only:
        query = query.filter(Employee.is_active == True)

    if department:
        query = query.filter(Employee.department == department)

    employees = query.all()
    return employees


@router.post(
    "/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED
)
async def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Create a new employee
    """
    # Check if employee ID or email already exists
    existing_employee = (
        db.query(Employee)
        .filter(
            (Employee.employee_id == employee.employee_id)
            | (Employee.email == employee.email)
        )
        .first()
    )

    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID or email already registered",
        )

    # Check if manager exists
    if employee.manager_id:
        manager = db.query(Employee).filter(Employee.id == employee.manager_id).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Manager not found"
            )

    # Create new employee
    new_employee = Employee(
        employee_id=employee.employee_id,
        name=employee.name,
        email=employee.email,
        hashed_password=get_password_hash(employee.password),
        department=employee.department,
        position=employee.position,
        manager_id=employee.manager_id,
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Get a specific employee by ID
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    return employee


@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Update an employee
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    # Update employee fields
    if employee_update.name is not None:
        employee.name = employee_update.name

    if employee_update.email is not None:
        # Check if email is being changed and if it's already in use
        if (
            employee_update.email != employee.email
            and db.query(Employee)
            .filter(Employee.email == employee_update.email)
            .first()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use"
            )
        employee.email = employee_update.email

    if employee_update.password is not None:
        employee.hashed_password = get_password_hash(employee_update.password)

    if employee_update.department is not None:
        employee.department = employee_update.department

    if employee_update.position is not None:
        employee.position = employee_update.position

    if employee_update.manager_id is not None:
        # Check if manager exists
        if employee_update.manager_id > 0:
            manager = (
                db.query(Employee)
                .filter(Employee.id == employee_update.manager_id)
                .first()
            )
            if not manager:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Manager not found"
                )
        employee.manager_id = (
            employee_update.manager_id if employee_update.manager_id > 0 else None
        )

    if employee_update.is_active is not None:
        employee.is_active = employee_update.is_active

    db.commit()
    db.refresh(employee)

    return employee


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Delete an employee (soft delete - set is_active to False)
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    # Soft delete by setting is_active to False
    employee.is_active = False
    db.commit()

    return None


@router.post("/employees/{employee_id}/reset-password", response_model=EmployeeResponse)
async def reset_employee_password(
    employee_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    """
    Reset an employee's password
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    employee.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(employee)

    return employee
