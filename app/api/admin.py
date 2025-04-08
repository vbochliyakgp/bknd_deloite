# app/api/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, get_current_active_admin
from app.models.employee import Employee, UserType
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeWithAnalytics
from app.core.security import get_password_hash
from fastapi import Body

router = APIRouter()


@router.get("/users", response_model=List[EmployeeWithAnalytics])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_admin),
):
    """
    Get all system users (HR and Admin)
    """
    print("Fetching all employees from the database...")
    query = db.query(Employee)

    employees = query.all()
    print(f"Total employees fetched: {len(employees)}")
    result = []

    for employee in employees:
        print(f"Processing employee: {employee.id} - {employee.name}")

        # Get latest vibemeter response
        latest_vibe = (
            db.query(VibemeterData)
            .filter(VibemeterData.employee_id == employee.id)
            .order_by(VibemeterData.date.desc())
            .first()
        )
        print(f"Latest vibe for employee {employee.id}: {latest_vibe}")

        # Get leave data
        leave_balance = 30  # Default annual leave
        leave_taken = (
            db.execute(
                text(
                    "SELECT SUM(leave_days) FROM leaves_data WHERE employee_id = :employee_id AND EXTRACT(YEAR FROM start_date) = EXTRACT(YEAR FROM CURRENT_DATE)"
                ),
                {"employee_id": employee.id},
            ).scalar()
            or 0
        )
        print(f"Leave taken for employee {employee.id}: {leave_taken}")
        leave_balance -= leave_taken
        print(f"Leave balance for employee {employee.id}: {leave_balance}")

        # Get activity data
        activity_data = db.execute(
            text(
                "SELECT hours_worked FROM activity_data WHERE employee_id = :employee_id ORDER BY date DESC LIMIT 3"
            ),
            {"employee_id": employee.id},
        ).all()
        # calculate average hours worked
        if activity_data:
            activity_data = sum([row[0] for row in activity_data]) / len(activity_data)
        else:
            activity_data = 0
        print(f"Average hours worked for employee {employee.id}: {activity_data}")

        # Get performance data
        performance = db.execute(
            text(
                "SELECT performance_rating FROM performance_data WHERE employee_id = :employee_id ORDER BY id DESC LIMIT 1"
            ),
            {"employee_id": employee.id},
        ).scalar()
        print(f"Latest performance rating for employee {employee.id}: {performance}")

        # Get rewards count
        rewards_count = (
            db.execute(
                text(
                    "SELECT COUNT(*) FROM rewards_data WHERE employee_id = :employee_id"
                ),
                {"employee_id": employee.id},
            ).scalar()
            or 0
        )
        print(f"Rewards count for employee {employee.id}: {rewards_count}")

        result.append(
            EmployeeWithAnalytics(
                **employee.__dict__,
                recent_vibe=str(latest_vibe.emotion_zone) if latest_vibe else None,
                leave_balance=leave_balance,
                average_hours_worked=round(activity_data, 1),
                latest_performance_rating=performance,
                rewards_count=rewards_count,
            )
        )

    print("Finished processing all employees.")
    return result

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
