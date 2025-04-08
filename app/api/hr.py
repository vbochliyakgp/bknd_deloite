# app/api/hr.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import pandas as pd
import io
import csv
from sqlalchemy import text
from typing import Dict

# Call OpenAI API using the client approach
from openai import AsyncOpenAI

from app.dependencies import get_db, get_current_active_hr
from app.core.security import get_password_hash
from app.models.employee import Employee, UserType, WellnessCheckStatus
from app.models.vibemeter import VibemeterData
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.models.leave import Leave
from app.models.activity import Activity
from app.models.onboarding import Onboarding
from app.models.performance import PerformanceData
from app.schemas.chat import MessageBaseNew
from app.models.rewards import Reward
from app.schemas.employee import EmployeeWithAnalytics
from app.schemas.analytics import (
    EmployeeAlert,
    EmployeeSessionAnalyticsNew,
    DailyReport,
)
from app.schemas.upload import DatasetType, UploadResponse, AtRiskEmployee
from app.schemas.chat import ChatSessionBaseNew
from app.services.analytics import AnalyticsService
from app.services.email import EmailService

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any
import openai

from app.database import get_db
from app.models.chat_session import ChatSession
from app.models.employee import Employee
from app.config import settings


# app/routes/dashboard.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.database import get_db
from app.models.employee import Employee, WellnessCheckStatus
from app.models.vibemeter import VibemeterData
from app.models.activity import Activity
from app.models.chat_session import ChatSession
from collections import defaultdict
from app.schemas.dashboard import (
    DashboardResponse,
    VibemeterTrendData,
    VibeDistribution,
)



router = APIRouter()


@router.get("/employees", response_model=List[EmployeeWithAnalytics])
async def get_all_employees(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Get all employees with basic analytics
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


@router.get(
    "/employees/{employee_id}/sessions", response_model=List[ChatSessionBaseNew]
)
async def get_employee_sessions(
    employee_id: str,
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
                session_id=session.session_id,
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
    employee_id: str,
    session_id: str,
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

    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.session_id == session.session_id)
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
    response_model=EmployeeSessionAnalyticsNew,
)
async def get_employee_analytics(
    employee_id: str,
    session_id: str,
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
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    print(f"Session details: {session.start_time} - {session.end_time}")
    analytics = EmployeeSessionAnalyticsNew(
        employee_id=employee_id,
        session_id=session.session_id,
        escalated=session.escalated,
        summary=session.summary,
        suggestions=session.suggestions,
        risk_score=session.risk_score,
        risk_factor=session.risk_factors,
        start_time=session.start_time,
        end_time=session.end_time,
    )
    return analytics


@router.post("/alerts/email/{employee_id}", status_code=status.HTTP_200_OK)
async def send_alert_email(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Send an alert email to an employee
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    success = await EmailService.send_employee_alert(
        db=db,
        employee_id=employee_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email",
        )

    return {"status": "success", "message": "Email sent successfully"}



@router.get("/reports/daily", response_model=DailyReport)
async def get_daily_report(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Get the daily report
    """
    # Get today's date
    today = datetime.now().date()

    # Query chat sessions that started today
    today_sessions = (
        db.query(
            ChatSession.employee_id,
            ChatSession.risk_score,
            ChatSession.suggestions,
            Employee.department,
        )
        .join(Employee, ChatSession.employee_id == Employee.id)
        .filter(func.date(ChatSession.start_time) == today)
        .filter(ChatSession.risk_score.isnot(None))  # Only sessions with risk scores
        .all()
    )

    session_data = []
    for session in today_sessions:
        # Extract risk factors from suggestions field (assuming they're stored as JSON or delimited text)
        risk_factors = extract_risk_factors(session.suggestions)

        session_data.append(
            {
                "employee_id": session.employee_id,
                "risk_score": session.risk_score,
                "risk_factors": session.risk_factors,
                "suggestions": session.suggestions,
                "department": session.department,
            }
        )

    # Format data as a table string for the prompt
    table_data = format_as_table(session_data)

    # Format data as a table string for the prompt
    table_data = format_as_table(session_data)

    print("Formatted table data for prompt:")
    print(table_data)

    # Read prompt template from file or use the provided one
    with open("app/prompts/daily_report_prompt.txt", "r") as f:
        prompt_template = f.read()

    # Replace placeholder with actual table data
    prompt = prompt_template.replace("[TABLE DATA WILL BE INSERTED HERE]", table_data)

    try:

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        print("API Key:", settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o",  # Use appropriate model
            messages=[{"role": "system", "content": prompt}],
            temperature=0.2,  # Lower temperature for more consistent output
            max_tokens=500,
            response_format={"type": "json_object"},
        )

        # Parse JSON response
        report_json = response.choices[0].message.content

        # Convert to Pydantic model for validation
        # This will raise a validation error if the structure doesn't match
        report = DailyReport.model_validate_json(report_json)

        return report

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating report: {str(e)}"
        )

#to be fixed
@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Get all dashboard data for the HR panel.
    """
    print("Fetching dashboard data...............................................")
       # Subquery to get the most recent vibe score for each employee
    subquery = (
        db.query(
            VibemeterData.employee_id,
            VibemeterData.vibe_score,
            func.row_number().over(
                partition_by=VibemeterData.employee_id,
                order_by=desc(VibemeterData.date)
            ).label("row_num")
        )
        .subquery()
    )
    
    # Get employees with their most recent vibe scores
    most_recent_vibes = db.query(subquery).filter(subquery.c.row_num == 1).all()
    
    # Calculate statistics
    high_vibe_count = 0  # vibe_score > 3
    low_vibe_count = 0   # vibe_score < 3
    vibe_distribution = defaultdict(int)
    
    for vibe in most_recent_vibes:
        if vibe.vibe_score > 3:
            high_vibe_count += 1
        elif vibe.vibe_score < 3:
            low_vibe_count += 1
        
        vibe_distribution[vibe.vibe_score] += 1
    
    # Get total number of chat sessions
    total_chat_sessions = db.query(func.count(ChatSession.session_id)).scalar() or 0
    
    # Get number of employees needing attention
    employees_needing_attention = (
        db.query(func.count(Employee.id))
        .filter(Employee.immediate_attention == True)
        .scalar() or 0
    )
    
    # Convert defaultdict to regular dict for JSON serialization
    vibe_score_distribution = dict(vibe_distribution)
    
    # Fill in missing scores (1-10) with 0 for better visualization
    for score in range(1, 11):
        if score not in vibe_score_distribution:
            vibe_score_distribution[score] = 0
    
    return {
        "employees_with_high_vibe": high_vibe_count,
        "employees_with_low_vibe": low_vibe_count,
        "total_chat_sessions": total_chat_sessions,
        "employees_needing_attention": employees_needing_attention,
        "vibe_score_distribution": vibe_score_distribution
    }



def extract_risk_factors(suggestions_text: str) -> List[str]:
    """
    Extract risk factors from the suggestions text.
    This function should be adapted based on how risk factors are actually stored.
    """
    if not suggestions_text:
        return []

    try:
        # Try parsing as JSON
        data = json.loads(suggestions_text)
        if isinstance(data, dict) and "risk_factors" in data:
            return data["risk_factors"]
        return []
    except json.JSONDecodeError:
        # If not JSON, assume comma-separated list
        return [factor.strip() for factor in suggestions_text.split(",")]


def format_as_table(session_data: List[Dict]) -> str:
    """
    Format the session data as a table string for the prompt.
    """
    if not session_data:
        return "No data available."

    # Create header
    table = "employee_id | risk_score | risk_factors | suggestions | department\n"
    table += "-----------|------------|--------------|------------|------------\n"

    # Add rows
    for session in session_data:
        risk_factors_str = (
            ", ".join(session["risk_factors"]) if session["risk_factors"] else "None"
        )
        suggestions_str = session["suggestions"] if session["suggestions"] else "None"
        department = session["department"] if session["department"] else "Unknown"

        table += f"{session['employee_id']} | {session['risk_score']} | {risk_factors_str} | {suggestions_str} | {department}\n"

    return table


def validate_report_structure(report: Dict[str, Any]) -> None:
    """
    Validate that the report has the required structure.
    """
    required_keys = [
        "report_date",
        "report_title",
        "executive_summary",
        "key_metrics",
        "key_insights",
        "top_risk_factors",
        "recommended_focus_areas",
    ]

    for key in required_keys:
        if key not in report:
            raise ValueError(f"Required key '{key}' missing from report")


@router.post("/upload", response_model=UploadResponse)
async def upload_data(
    files: List[UploadFile] = File(...),
    dataset_types: List[str] = Form(...),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_active_hr),
):
    """
    Upload multiple data files (CSV), one for each dataset type
    """
    if len(files) != len(dataset_types):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of files and dataset types must match",
        )

    processed_data = {}

    for file, dataset_type_str in zip(files, dataset_types):
        if file.content_type != "text/csv":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} is not a CSV file",
            )

        try:
            # Validate and convert dataset type
            try:
                dataset_type = DatasetType(dataset_type_str)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid dataset type: {dataset_type_str}",
                )

            contents = await file.read()

            # Parse CSV data
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

            if dataset_type == DatasetType.LEAVE:
                processed_data[DatasetType.LEAVE] = await process_leave_data(db, df)
            elif dataset_type == DatasetType.ACTIVITY:
                processed_data[DatasetType.ACTIVITY] = await process_activity_data(
                    db, df
                )
            elif dataset_type == DatasetType.REWARDS:
                processed_data[DatasetType.REWARDS] = await process_rewards_data(db, df)
            elif dataset_type == DatasetType.PERFORMANCE:
                processed_data[DatasetType.PERFORMANCE] = (
                    await process_performance_data(db, df)
                )
            elif dataset_type == DatasetType.VIBEMETER:
                processed_data[DatasetType.VIBEMETER] = await process_vibemeter_data(
                    db, df
                )
            elif dataset_type == DatasetType.ONBOARDING:
                processed_data[DatasetType.ONBOARDING] = await process_onboarding_data(
                    db, df
                )

        except Exception as e:

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing file {file.filename}: {str(e)}",
            )

    # Analyze vibemeter data
    vibemeter_analysis = await analyze_vibemeter(processed_data)

    at_risk_employees = []

    if vibemeter_analysis:
        for employee in vibemeter_analysis:
            employee_id = employee["Employee_ID"]
            # Update employee's immediate attention status
            db.query(Employee).filter(Employee.employee_id == employee_id).update(
                {"immediate_attention": True}
            )
            at_risk_employees.append(AtRiskEmployee(employee_id=employee_id))

        db.commit()

    return UploadResponse(at_risk_employees=at_risk_employees)


async def analyze_vibemeter(dfs: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
    """
    Analyze vibemeter data and return employees who need attention
    """
    # Implement vibemeter analysis logic
    low_vibe_json = []
    high_emotion_diff_json = []

    # Example logic to identify employees with low vibe scores
    vibemeter = dfs.get(DatasetType.VIBEMETER)

    if not pd.isna(vibemeter["Employee_ID"].iloc[0]) and not str(
        vibemeter["Employee_ID"].iloc[0]
    ).startswith("EMP"):
        vibemeter["Employee_ID"] = vibemeter["Employee_ID"].apply(
            lambda x: f"EMP{x:04d}"
        )

        # Count occurrences of each employee ID
    counts = vibemeter["Employee_ID"].value_counts()

    # Identify employees with single vs multiple entries
    unique = counts[counts == 1].index
    multiple = counts[counts > 1].index

    # Split dataframe based on entry count
    vibe_unique = vibemeter[vibemeter["Employee_ID"].isin(unique)]
    vibe_multi = vibemeter[vibemeter["Employee_ID"].isin(multiple)]

    # Analyze emotional variability for employees with multiple entries
    result = []
    for emp_id, group in vibe_multi.groupby("Employee_ID"):
        scores = group["Vibe_Score"].values
        if len(scores) == 2:
            diff = abs(scores[0] - scores[1])
        else:
            mean_score = scores.mean()
            diff = abs((scores - mean_score)).mean()
        result.append({"Employee_ID": emp_id, "emotion_diff": diff})

    vibe_emotion_diff = pd.DataFrame(result)

    # Identify employees with low vibe scores (bottom 40%)
    low_vibe_df = vibe_unique[
        vibe_unique["Vibe_Score"] < vibe_unique["Vibe_Score"].quantile(0.40)
    ][["Employee_ID"]]

    # Identify employees with high emotional variability (top 15%)
    high_emotion_diff_df = vibe_emotion_diff[
        vibe_emotion_diff["emotion_diff"]
        > vibe_emotion_diff["emotion_diff"].quantile(0.85)
    ][["Employee_ID"]]

    # Convert to JSON format
    low_vibe_json = low_vibe_df.to_dict(orient="records")
    high_emotion_diff_json = high_emotion_diff_df.to_dict(orient="records")

    # Combine both lists
    all_employees = low_vibe_json + high_emotion_diff_json

    # Remove duplicates by converting to a dictionary and back to a list add to database
    unique_employees = list({emp["Employee_ID"]: emp for emp in all_employees}.values())

    return unique_employees


async def process_leave_data(db: Session, df: pd.DataFrame) -> pd.DataFrame:
    """
    Process leave data from CSV
    """
    # Implement data import logic for leaves
    for _, row in df.iterrows():
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == row["Employee_ID"])
            .first()
        )
        if not employee:
            # insert new employee with dummy data
            employee = Employee(
                employee_id=str(row["Employee_ID"]),
                name="Jake Doe",  # Placeholder, should be replaced with actual name
                email="jakedoe@example.com",
                hashed_password=get_password_hash("dummyhashedpassword"),
                phone="1234567890",
                department="HR",
                position="HR Manager",
                user_type=UserType.employee,
                profile_image=None,
                wellness_check_status=WellnessCheckStatus.not_received,
                last_vibe="neutral",
                immediate_attention=False,
            )

            db.add(employee)
            db.commit()
            db.refresh(employee)
            # Refresh the employee object to get the new ID

        # leave = Leave(
        #     employee_id=str(employee.id),
        #     leave_type=str(row["leave_type"]),
        #     start_date=datetime.strptime(row["start_date"], "%Y-%m-%d").date(),
        #     end_date=datetime.strptime(row["end_date"], "%Y-%m-%d").date(),
        #     leave_days=int(row["leave_days"]),
        # )

        # db.add(leave)
        db.execute(
            text("INSERT INTO leaves_data (employee_id, leave_type, start_date, end_date, leave_days) VALUES (:employee_id, :leave_type, :start_date, :end_date, :leave_days)"),
            {
                "employee_id": str(employee.id),
                "leave_type": str(row["Leave_Type"]),
                "start_date": datetime.strptime(row["Leave_Start_Date"], "%Y-%m-%d").date(),
                "end_date": datetime.strptime(row["Leave_End_Date"], "%Y-%m-%d").date(),
                "leave_days": int(row["Leave_Days"]),
            }
        )

    db.commit()
    return df


async def process_activity_data(db: Session, df: pd.DataFrame) -> pd.DataFrame:
    """
    Process activity data from CSV
    """
    # Implement data import logic for activities
    for _, row in df.iterrows():
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == row["Employee_ID"])
            .first()
        )
        if not employee:
            employee = Employee(
                employee_id=str(row["Employee_ID"]),
                name="Jake Doe",  # Placeholder, should be replaced with actual name
                email="jakedoe@example.com",
                hashed_password=get_password_hash("dummyhashedpassword"),
                phone="1234567890",
                department="HR",
                position="HR Manager",
                user_type=UserType.employee,
                profile_image=None,
                wellness_check_status=WellnessCheckStatus.not_received,
                last_vibe="neutral",
                immediate_attention=False,
            )

            db.add(employee)
            db.commit()
            db.refresh(employee)
            # Refresh the employee object to get the new ID

        # activity = Activity(
        #     employee_id=str(employee.id),
        #     date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
        #     hours_worked=float(row["hours_worked"]),
        #     meetings_attended=int(row["meetings_attended"]),
        #     emails_sent=int(row["emails_sent"]),
        #     teams_messages_sent=int(row["teams_messages_sent"]),
        # )

        # db.add(activity)
        db.execute(
            text("INSERT INTO activity_data (employee_id, date, hours_worked, meetings_attended, emails_sent, teams_messages_sent) VALUES (:employee_id, :date, :hours_worked, :meetings_attended, :emails_sent, :teams_messages_sent)"),
            {
                "employee_id": str(employee.id),
                "date": datetime.strptime(row["Date"], "%Y-%m-%d").date(),
                "hours_worked": float(row["Work_Hours"]),
                "meetings_attended": int(row["Meetings_Attended"]),
                "emails_sent": int(row["Emails_Sent"]),
                "teams_messages_sent": int(row["Teams_Messages_Sent"]),
            }
        )

    db.commit()
    return df


async def process_rewards_data(db: Session, df: pd.DataFrame) -> pd.DataFrame:
    """
    Process rewards data from CSV
    """
    # Implement data import logic for rewards
    for _, row in df.iterrows():
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == row["Employee_ID"])
            .first()
        )
        if not employee:
            employee = Employee(
                employee_id=str(row["Employee_ID"]),
                name="Jake Doe",  # Placeholder, should be replaced with actual name
                email="jakedoe@example.com",
                hashed_password=get_password_hash("dummyhashedpassword"),
                phone="1234567890",
                department="HR",
                position="HR Manager",
                user_type=UserType.employee,
                profile_image=None,
                wellness_check_status=WellnessCheckStatus.not_received,
                last_vibe="neutral",
                immediate_attention=False,
            )

            db.add(employee)
            db.commit()
            db.refresh(employee)
            # Refresh the employee object to get the new ID

        # reward = Reward(
        #     employee_id=str(employee.id),
        #     reward_type=str(row["Award_Type"]),
        #     reward_date=datetime.strptime(row["Award_Date"], "%Y-%m-%d").date(),
        #     points=int(row["Reward_Points"]),
        # )

        # db.add(reward)
        db.execute(
            text("INSERT INTO rewards_data (employee_id, reward_type, reward_date, points) VALUES (:employee_id, :reward_type, :reward_date, :points)"),
            {
                "employee_id": str(employee.id),
                "reward_type": str(row["Award_Type"]),
                "reward_date": datetime.strptime(row["Award_Date"], "%Y-%m-%d").date(),
                "points": int(row["Reward_Points"]),
            }
        )

    db.commit()
    return df


async def process_performance_data(db: Session, df: pd.DataFrame) -> pd.DataFrame:
    """
    Process performance data from CSV
    """
    # Implement data import logic for performance
    for _, row in df.iterrows():
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == row["Employee_ID"])
            .first()
        )
        if not employee:
            employee = Employee(
                employee_id=str(row["Employee_ID"]),
                name="Jake Doe",  # Placeholder, should be replaced with actual name
                email="jakedoe@example.com",
                hashed_password=get_password_hash("dummyhashedpassword"),
                phone="1234567890",
                department="HR",
                position="HR Manager",
                user_type=UserType.employee,
                profile_image=None,
                wellness_check_status=WellnessCheckStatus.not_received,
                last_vibe="neutral",
                immediate_attention=False,
            )

            db.add(employee)
            db.commit()
            db.refresh(employee)
            # Refresh the employee object to get the new ID

        # performance = PerformanceData(
        #     employee_id=str(employee.id),
        #     review_period=str(row["Review_Period"]),
        #     performance_rating=int(row["Performance_Rating"]),
        #     manager_feedback=str(row["Manager_Feedback"]),
        #     promotion_consideration=bool(row["Promotion_Consideration"]),
        # )

        # db.add(performance)
        db.execute(
            text("INSERT INTO performance_data (employee_id, review_period, performance_rating, manager_feedback, promotion_consideration) VALUES (:employee_id, :review_period, :performance_rating, :manager_feedback, :promotion_consideration)"),
            {
                "employee_id": str(employee.id),
                "review_period": str(row["Review_Period"]),
                "performance_rating": int(row["Performance_Rating"]),
                "manager_feedback": str(row["Manager_Feedback"]),
                "promotion_consideration": bool(row["Promotion_Consideration"]),
            }
        )

    db.commit()
    return df


async def process_vibemeter_data(db: Session, df: pd.DataFrame) -> pd.DataFrame:
    """
    Process vibemeter data from CSV
    """
    # Implement data import logic for vibemeter responses
    for _, row in df.iterrows():
        employee = (
            db.query(Employee)
            .filter(Employee.employee_id == row["Employee_ID"])
            .first()
        )
        if not employee:
            employee = Employee(
                employee_id=str(row["Employee_ID"]),
                name="Jake Doe",  # Placeholder, should be replaced with actual name
                email="jakedoe@example.com",
                hashed_password=get_password_hash("dummyhashedpassword"),
                phone="1234567890",
                department="HR",
                position="HR Manager",
                user_type=UserType.employee,
                profile_image=None,
                wellness_check_status=WellnessCheckStatus.not_received,
                last_vibe="neutral",
                immediate_attention=False,
            )

            db.add(employee)
            db.commit()
            db.refresh(employee)
            # Refresh the employee object to get the new ID

        # Convert string emotion to EmotionZone enum

        # vibemeter_response = VibemeterData(
        #     employee_id=str(employee.id),
        #     date=datetime.strptime(row["Response_Date"], "%Y-%m-%d").date(),
        #     vibe_score=int(row["Vibe_Score"]),
        #     emotion_zone=str(row["Emotion_Zone"]),
        # )

        # db.add(vibemeter_response)
        db.execute(
            text("INSERT INTO vibemeter_data (employee_id, date, vibe_score, emotion_zone) VALUES (:employee_id, :date, :vibe_score, :emotion_zone)"),
            {
                "employee_id": str(employee.id),
                "date": datetime.strptime(row["Response_Date"], "%Y-%m-%d").date(),
                "vibe_score": int(row["Vibe_Score"]),
                "emotion_zone": str(row["Emotion_Zone"]),
            }
        )

    db.commit()
    return df


async def process_onboarding_data(db: Session, df: pd.DataFrame) -> pd.DataFrame:
    """
    Process onboarding data from CSV - this would typically create new employees
    """
    # Implement data import logic for new employees (onboarding)

    for _, row in df.iterrows():
        # Check if employee already exists
        existing = (
            db.query(Employee)
            .filter(Employee.employee_id == row["Employee_ID"])
            .first()
        )
        if existing:
            employee = Employee(
                employee_id=str(row["Employee_ID"]),
                name="Jake Doe",  # Placeholder, should be replaced with actual name
                email="jakedoe@example.com",
                hashed_password=get_password_hash("dummyhashedpassword"),
                phone="1234567890",
                department="HR",
                position="HR Manager",
                user_type=UserType.employee,
                profile_image=None,
                wellness_check_status=WellnessCheckStatus.not_received,
                last_vibe="neutral",
                immediate_attention=False,
            )

            db.add(employee)
            db.commit()
            db.refresh(employee)
            # Refresh the employee object to get the new ID

        # Create new employee
        # employee = Onboarding(
        #     employee_id=str(row["Employee_ID"]),
        #     onboarding_feedback=str(row["Onboarding_Feedback"]),
        #     joining_date=datetime.strptime(row["Joining_Date"], "%Y-%m-%d").date(),
        #     mentor_assigned=bool(row["Mentor_Assigned"]),
        #     training_completed=bool(row["Training_Completed"]),
        # )

        # db.add(employee)

        db.execute(
            text("INSERT INTO onboarding_data (employee_id, onboarding_feedback, joining_date, mentor_assigned, training_completed) VALUES (:employee_id, :onboarding_feedback, :joining_date, :mentor_assigned, :training_completed)"),
            {
                "employee_id": str(employee.id),
                "onboarding_feedback": str(row["Onboarding_Feedback"]),
                "joining_date": datetime.strptime(row["Joining_Date"], "%Y-%m-%d").date(),
                "mentor_assigned": bool(row["Mentor_Assigned"]),
                "training_completed": bool(row["Training_Completed"]),
            }
        )

    db.commit()

    return df
