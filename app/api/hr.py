# app/api/hr.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import pandas as pd
import io
import csv
from sqlalchemy import text
from pydantic import TypeAdapter

from app.dependencies import get_db, get_current_active_hr
from app.models.employee import Employee
from app.models.vibemeter import VibemeterData, EmotionZone
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.models.leave import Leave, LeaveStatus, LeaveType
from app.models.activity import Activity
from app.models.performance import Performance
from app.schemas.chat import MessageResponse, MessageBaseNew
from app.models.rewards import Reward
from app.schemas.employee import EmployeeResponse, EmployeeWithAnalytics
from app.schemas.analytics import (
    EmployeeAlert,
    EmployeeSessionAnalytics,
    DailyReport,
    SendEmailAlert,
)
from app.schemas.upload import DatasetType, UploadResponse
from app.schemas.chat import ChatSessionWithMessages, ChatSessionBaseNew
from app.services.analytics import AnalyticsService
from app.services.email import EmailService

router = APIRouter()


@router.get("/employees", response_model=List[EmployeeWithAnalytics])
async def get_all_employees(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Get all employees with basic analytics
    """
    query = db.query(Employee)

    employees = query.all()
    result = []

    for employee in employees:
        # Get latest vibemeter response
        latest_vibe = (
            db.query(VibemeterData)
            .filter(VibemeterData.employee_id == employee.id)
            .order_by(VibemeterData.response_date.desc())
            .first()
        )

        # Get leave data
        leave_balance = 30  # Default annual leave
        leave_taken = (
            db.execute(
                text(
                    "SELECT SUM(leave_days) FROM leaves WHERE employee_id = :employee_id AND EXTRACT(YEAR FROM start_date) = EXTRACT(YEAR FROM CURRENT_DATE)"
                ),
                {"employee_id": employee.id},
            ).scalar()
            or 0
        )
        leave_balance -= leave_taken

        # Get activity data
        activity_data = (
            db.execute(
                text(
                    "SELECT AVG(hours_worked) FROM activities WHERE employee_id = :employee_id ORDER BY date DESC LIMIT 3"
                ),
                {"employee_id": employee.id},
            ).scalar()
            or 0
        )

        # Get performance data
        performance = db.execute(
            text(
                "SELECT performance_rating FROM performances WHERE employee_id = :employee_id ORDER BY review_date DESC LIMIT 1"
            ),
            {"employee_id": employee.id},
        ).scalar()

        # Get rewards count
        rewards_count = (
            db.execute(
                text("SELECT COUNT(*) FROM rewards WHERE employee_id = :employee_id"),
                {"employee_id": employee.id},
            ).scalar()
            or 0
        )

        result.append(
            EmployeeWithAnalytics(
                **employee.__dict__,
                recent_vibe=latest_vibe.emotion_zone if latest_vibe else None,
                leave_balance=leave_balance,
                average_hours_worked=round(activity_data, 1),
                latest_performance_rating=performance,
                rewards_count=rewards_count,
            )
        )

    return result


@router.get(
    "/employees/{employee_id}/sessions", response_model=List[ChatSessionBaseNew]
)
async def get_employee_sessions(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Get chat sessions for a specific employee
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.employee_id == employee_id)
        .order_by(ChatSession.start_time.desc())
        .all()
    )

    result = []
    for session in sessions:
        result.append(
            ChatSessionBaseNew(
                employee_id=session.employee_id,
                session_id=session.id,
                start_time=session.start_time,
                end_time=session.end_time,
            )
        )

    return result


@router.get(
    "/employees/{employee_id}/messages/{session_id}",
    response_model=List[MessageBaseNew],
)
async def get_employee_messages(
    employee_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Get messages for a specific chat session of an employee
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.session_id == session.id)
        .order_by(Message.id)
        .all()
    )

    result = []
    for i, message in enumerate(messages):
        result.append(
            MessageBaseNew(
                session_id=message.session_id,
                serial_number=i + 1,
                question=message.question,
                answer=message.answer,
            )
        )

    return result


@router.get(
    "/employees/{employee_id}/analytics/{session_id}",
    response_model=EmployeeSessionAnalytics,
)
async def get_employee_analytics(
    employee_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Get detailed analytics for a specific employee
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    # TO DO: Implement detailed analytics logic
    analytics = AnalyticsService.get_employee_analytics(db, employee_id, session_id)
    return analytics


@router.get("/alerts", response_model=List[EmployeeAlert])
async def get_employee_alerts(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Get alerts for employees who need attention
    """
    alerts = AnalyticsService.identify_at_risk_employees(db)
    return alerts


@router.post("/alerts/email", status_code=status.HTTP_200_OK)
async def send_alert_email(
    alert: SendEmailAlert,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Send an alert email to an employee
    """
    employee = db.query(Employee).filter(Employee.id == alert.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    success = await EmailService.send_employee_alert(
        db=db,
        employee_id=alert.employee_id,
        subject=alert.subject,
        message=alert.message,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email",
        )

    return {"status": "success", "message": "Email sent successfully"}


@router.get("/reports/daily", response_model=DailyReport)
async def get_daily_report(
    report_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Get the daily report
    """
    if not report_date:
        report_date = date.today()

    report = AnalyticsService.generate_daily_report(db, report_date)
    return report


@router.post("/upload", response_model=UploadResponse)
async def upload_data(
    file: UploadFile = File(...),
    dataset_type: DatasetType = Form(...),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Upload data file (CSV)
    """
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )

    contents = await file.read()

    try:
        # Parse CSV data
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        rows_processed = 0

        if dataset_type == DatasetType.LEAVE:
            rows_processed = await process_leave_data(db, df)
        elif dataset_type == DatasetType.ACTIVITY:
            rows_processed = await process_activity_data(db, df)
        elif dataset_type == DatasetType.REWARDS:
            rows_processed = await process_rewards_data(db, df)
        elif dataset_type == DatasetType.PERFORMANCE:
            rows_processed = await process_performance_data(db, df)
        elif dataset_type == DatasetType.VIBEMETER:
            rows_processed = await process_vibemeter_data(db, df)
        elif dataset_type == DatasetType.ONBOARDING:
            rows_processed = await process_onboarding_data(db, df)

        return UploadResponse(
            filename=str(file.filename),
            dataset_type=dataset_type,
            rows_processed=rows_processed,
            success=True,
            message=f"Successfully processed {rows_processed} rows",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}",
        )


async def process_leave_data(db: Session, df: pd.DataFrame) -> int:
    """
    Process leave data from CSV
    """
    # Implement data import logic for leaves
    for _, row in df.iterrows():
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == row["employee_id"])
            .first()
        )
        if not employee:
            continue

        leave = Leave(
            employee_id=employee.id,
            leave_type=row["leave_type"],
            start_date=datetime.strptime(row["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(row["end_date"], "%Y-%m-%d").date(),
            status=row["status"],
            reason=row.get("reason", None),
        )

        db.add(leave)

    db.commit()
    return len(df)


async def process_activity_data(db: Session, df: pd.DataFrame) -> int:
    """
    Process activity data from CSV
    """
    # Implement data import logic for activities
    for _, row in df.iterrows():
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == row["employee_id"])
            .first()
        )
        if not employee:
            continue

        activity = Activity(
            employee_id=employee.id,
            date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
            hours_worked=float(row["hours_worked"]),
            meetings_attended=int(row["meetings_attended"]),
            emails_sent=int(row["emails_sent"]),
            after_hours_work=float(row["after_hours_work"]),
        )

        db.add(activity)

    db.commit()
    return len(df)


async def process_rewards_data(db: Session, df: pd.DataFrame) -> int:
    """
    Process rewards data from CSV
    """
    # Implement data import logic for rewards
    for _, row in df.iterrows():
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == row["employee_id"])
            .first()
        )
        if not employee:
            continue

        reward = Reward(
            employee_id=employee.id,
            reward_type=row["reward_type"],
            reward_date=datetime.strptime(row["reward_date"], "%Y-%m-%d").date(),
            amount=(
                int(row["amount"])
                if "amount" in row and not pd.isna(row["amount"])
                else None
            ),
            description=row["description"],
            awarded_by=(
                int(row["awarded_by"])
                if "awarded_by" in row and not pd.isna(row["awarded_by"])
                else None
            ),
        )

        db.add(reward)

    db.commit()
    return len(df)


async def process_performance_data(db: Session, df: pd.DataFrame) -> int:
    """
    Process performance data from CSV
    """
    # Implement data import logic for performance
    for _, row in df.iterrows():
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == row["employee_id"])
            .first()
        )
        if not employee:
            continue

        performance = Performance(
            employee_id=employee.id,
            review_period=row["review_period"],
            rating=float(row["rating"]),
            review_date=datetime.strptime(row["review_date"], "%Y-%m-%d").date(),
            reviewer_id=(
                int(row["reviewer_id"])
                if "reviewer_id" in row and not pd.isna(row["reviewer_id"])
                else None
            ),
            promotion_eligible=(
                bool(row["promotion_eligible"])
                if "promotion_eligible" in row
                else False
            ),
            strengths=row.get("strengths", None),
            areas_for_improvement=row.get("areas_for_improvement", None),
            comments=row.get("comments", None),
        )

        db.add(performance)

    db.commit()
    return len(df)


async def process_vibemeter_data(db: Session, df: pd.DataFrame) -> int:
    """
    Process vibemeter data from CSV
    """
    # Implement data import logic for vibemeter responses
    for _, row in df.iterrows():
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == row["employee_id"])
            .first()
        )
        if not employee:
            continue

        # Convert string emotion to EmotionZone enum
        emotion = row["emotion_zone"]
        if emotion not in [e.value for e in EmotionZone]:
            continue

        vibemeter_response = VibemeterResponse(
            employee_id=employee.id,
            response_date=datetime.strptime(row["response_date"], "%Y-%m-%d").date(),
            emotion_zone=emotion,
            comment=row.get("comment", None),
        )

        db.add(vibemeter_response)

    db.commit()
    return len(df)


async def process_onboarding_data(db: Session, df: pd.DataFrame) -> int:
    """
    Process onboarding data from CSV - this would typically create new employees
    """
    # Implement data import logic for new employees (onboarding)
    from app.core.security import get_password_hash

    rows_processed = 0
    for _, row in df.iterrows():
        # Check if employee already exists
        existing = (
            db.query(Employee)
            .filter(Employee.employee_id == row["employee_id"])
            .first()
        )
        if existing:
            continue

        # Create new employee
        employee = Employee(
            employee_id=row["employee_id"],
            name=row["name"],
            email=row["email"],
            hashed_password=get_password_hash(row["default_password"]),
            department=row["department"],
            position=row["position"],
            manager_id=None,  # We'll update this later
        )

        db.add(employee)
        rows_processed += 1

    db.commit()

    # Second pass to update manager relationships
    for _, row in df.iterrows():
        if "manager_id" in row and not pd.isna(row["manager_id"]):
            employee = (
                db.query(Employee)
                .filter(Employee.employee_id == row["employee_id"])
                .first()
            )
            manager = (
                db.query(Employee)
                .filter(Employee.employee_id == row["manager_id"])
                .first()
            )

            if employee and manager:
                employee.manager_id = manager.id

    db.commit()
    return rows_processed
