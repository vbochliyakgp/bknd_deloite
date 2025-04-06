# app/services/analytics.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from collections import Counter

from app.models.employee import Employee
from app.models.vibemeter import VibemeterResponse, EmotionZone
from app.models.leave import Leave
from app.models.activity import Activity
from app.models.performance import Performance
from app.models.rewards import Reward
from app.models.chat_session import ChatSession, SessionStatus
from app.schemas.analytics import EmployeeAlert, EmployeeSessionAnalytics, DailyReport


class AnalyticsService:
    @staticmethod
    def get_employee_data(db: Session, employee_id: int) -> Dict[str, Any]:
        """
        Get comprehensive data for a single employee
        """
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {}

        # Get vibemeter data
        vibe_history = (
            db.query(VibemeterResponse)
            .filter(VibemeterResponse.employee_id == employee_id)
            .order_by(desc(VibemeterResponse.response_date))
            .limit(30)
            .all()
        )

        # Get leave data
        leave_data = db.query(Leave).filter(Leave.employee_id == employee_id).all()
        leave_balance = 30  # Assuming default annual leave balance
        leave_taken = sum(
            (l.end_date - l.start_date).days + 1
            for l in leave_data
            if l.start_date.year == date.today().year
        )
        leave_balance -= leave_taken

        # Get activity data
        activity_data = (
            db.query(Activity)
            .filter(Activity.employee_id == employee_id)
            .filter(Activity.date >= date.today() - timedelta(days=30))
            .all()
        )
        avg_hours = sum(a.hours_worked.scalar() for a in activity_data) / (
            len(activity_data) or 1
        )
        avg_after_hours = sum(a.after_hours_work.scalar() for a in activity_data) / (
            len(activity_data) or 1
        )

        # Get performance data
        latest_performance = (
            db.query(Performance)
            .filter(Performance.employee_id == employee_id)
            .order_by(desc(Performance.review_date))
            .first()
        )

        # Get rewards data
        rewards = (
            db.query(Reward)
            .filter(Reward.employee_id == employee_id)
            .order_by(desc(Reward.reward_date))
            .all()
        )

        return {
            "name": employee.name,
            "department": employee.department,
            "position": employee.position,
            "vibe_history": [
                {
                    "date": v.response_date.strftime("%Y-%m-%d"),
                    "emotion": v.emotion_zone,
                }
                for v in vibe_history
            ],
            "leave_data": {
                "balance": leave_balance,
                "taken": leave_taken,
                "details": [
                    {
                        "start_date": l.start_date.strftime("%Y-%m-%d"),
                        "end_date": l.end_date.strftime("%Y-%m-%d"),
                        "type": l.leave_type,
                        "status": l.status,
                    }
                    for l in leave_data
                ],
            },
            "activity_data": {
                "average_hours": round(avg_hours, 2),
                "average_after_hours": round(avg_after_hours, 2),
                "details": [
                    {
                        "date": a.date.strftime("%Y-%m-%d"),
                        "hours": a.hours_worked,
                        "after_hours": a.after_hours_work,
                        "meetings": a.meetings_attended,
                    }
                    for a in activity_data
                ],
            },
            "performance_data": {
                "rating": latest_performance.rating if latest_performance else None,
                "review_period": (
                    latest_performance.review_period if latest_performance else None
                ),
                "promotion_eligible": (
                    latest_performance.promotion_eligible
                    if latest_performance
                    else None
                ),
            },
            "rewards_data": {
                "count": len(rewards),
                "recent_rewards": [
                    {
                        "type": r.reward_type,
                        "date": r.reward_date.strftime("%Y-%m-%d"),
                        "description": r.description,
                    }
                    for r in rewards[:3]
                ],
            },
        }

    @staticmethod
    def get_employee_analytics(
        db: Session, employee_id: int
    ) -> EmployeeSessionAnalytics:
        """
        Get detailed analytics for an employee including all metrics and sessions
        """
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return None

        # Get basic employee data
        employee_data = AnalyticsService.get_employee_data(db, employee_id)

        # Get chat sessions
        sessions = (
            db.query(ChatSession)
            .filter(ChatSession.employee_id == employee_id)
            .order_by(desc(ChatSession.start_time))
            .all()
        )

        # Calculate session metrics
        session_count = len(sessions)
        session_lengths = [
            (
                (s.end_time - s.start_time).total_seconds() / 60
                if s.end_time.scalar()
                else (datetime.now() - s.start_time).total_seconds() / 60
            )
            for s in sessions
        ]
        avg_session_length = (
            sum(session_lengths) / len(session_lengths) if session_lengths else 0
        )

        # Get emotion trend
        vibe_responses = (
            db.query(VibemeterResponse)
            .filter(VibemeterResponse.employee_id == employee_id)
            .order_by(VibemeterResponse.response_date)
            .all()
        )

        emotion_counts = Counter([v.emotion_zone for v in vibe_responses])
        most_common_emotion = (
            emotion_counts.most_common(1)[0][0] if emotion_counts else "Unknown"
        )

        emotion_trend = []
        for i in range(0, len(vibe_responses), 5):  # Group by 5 days
            batch = vibe_responses[i : i + 5]
            emotion_trend.append(
                {
                    "period": f"{batch[0].response_date} to {batch[-1].response_date}",
                    "emotions": Counter([v.emotion_zone for v in batch]),
                }
            )

        # Identify risk factors
        risk_factors = []

        # Check recent emotions
        recent_vibes = [v.emotion_zone for v in vibe_responses[-10:] if v]
        negative_emotions_count = sum(
            1 for e in recent_vibes if e in [EmotionZone.FRUSTRATED, EmotionZone.SAD]
        )
        if negative_emotions_count >= 3 and len(recent_vibes) >= 5:
            risk_factors.append("High frequency of negative emotions")

        # Check work hours
        if employee_data["activity_data"]["average_hours"] > 10:
            risk_factors.append("Consistently long working hours")

        if employee_data["activity_data"]["average_after_hours"] > 2:
            risk_factors.append("Significant after-hours work")

        # Check leave balance
        if employee_data["leave_data"]["balance"] > 20:
            risk_factors.append("Unused leave accumulation")

        # Check performance rating
        if (
            employee_data["performance_data"]["rating"]
            and employee_data["performance_data"]["rating"] < 3
        ):
            risk_factors.append("Below average performance rating")

        # Generate recommendations
        recommendations = []
        if "High frequency of negative emotions" in risk_factors:
            recommendations.append(
                "Schedule a one-on-one wellness check with manager or HR"
            )

        if (
            "Consistently long working hours" in risk_factors
            or "Significant after-hours work" in risk_factors
        ):
            recommendations.append(
                "Evaluate workload distribution and consider reallocation"
            )

        if "Unused leave accumulation" in risk_factors:
            recommendations.append(
                "Encourage taking planned time off for work-life balance"
            )

        if "Below average performance rating" in risk_factors:
            recommendations.append("Set up additional training or mentoring support")

        return EmployeeSessionAnalytics(
            employee_id=employee.id.scalar(),
            employee_name=employee.name.scalar(),
            session_count=session_count,
            average_session_length=round(avg_session_length, 2),
            most_common_emotion=most_common_emotion,
            emotion_trend=emotion_trend,
            leave_usage=employee_data["leave_data"],
            activity_metrics=employee_data["activity_data"],
            performance_data=employee_data["performance_data"],
            rewards_data=employee_data["rewards_data"],
            risk_factors=risk_factors,
            recommended_actions=recommendations,
        )

    @staticmethod
    def identify_at_risk_employees(db: Session) -> List[EmployeeAlert]:
        """
        Identify employees who need attention based on various metrics
        """
        alerts = []

        # Get all active employees
        employees = db.query(Employee).filter(Employee.is_active == True).all()

        for employee in employees:
            # Get recent vibe responses (last 10 days)
            recent_vibes = (
                db.query(VibemeterResponse)
                .filter(VibemeterResponse.employee_id == employee.id)
                .filter(
                    VibemeterResponse.response_date >= date.today() - timedelta(days=10)
                )
                .order_by(VibemeterResponse.response_date)
                .all()
            )

            # Check for consistently negative emotions
            negative_emotions = [
                v
                for v in recent_vibes
                if v.emotion_zone in [EmotionZone.FRUSTRATED, EmotionZone.SAD]
            ]
            if len(negative_emotions) >= 3 and len(recent_vibes) >= 5:
                alerts.append(
                    EmployeeAlert(
                        employee_id=employee.id.scalar(),
                        employee_name=employee.name.scalar(),
                        alert_type="Emotional Well-being",
                        alert_reason=f"Employee has reported {len(negative_emotions)} negative emotions in the last 10 days",
                        alert_date=date.today(),
                        alert_severity=(
                            "High" if len(negative_emotions) >= 4 else "Medium"
                        ),
                        recommended_action="Schedule a wellness check-in",
                    )
                )

            # Check for long working hours
            recent_activity = (
                db.query(Activity)
                .filter(Activity.employee_id == employee.id)
                .filter(Activity.date >= date.today() - timedelta(days=7))
                .all()
            )

            if recent_activity:
                avg_hours = sum(a.hours_worked.scalar() for a in recent_activity) / len(
                    recent_activity
                )
                if avg_hours > 10:
                    alerts.append(
                        EmployeeAlert(
                            employee_id=employee.id.scalar(),
                            employee_name=employee.name.scalar(),
                            alert_type="Workload",
                            alert_reason=f"Employee has been averaging {avg_hours:.1f} hours/day in the last week",
                            alert_date=date.today(),
                            alert_severity="High" if avg_hours > 12 else "Medium",
                            recommended_action="Review workload allocation",
                        )
                    )

            # Check for unused leave
            leave_records = (
                db.query(Leave).filter(Leave.employee_id == employee.id).all()
            )
            leave_taken = sum(
                (l.end_date - l.start_date).days + 1
                for l in leave_records
                if l.start_date.year == date.today().year
            )

            months_passed = date.today().month
            if months_passed > 6 and leave_taken < 5:
                alerts.append(
                    EmployeeAlert(
                        employee_id=employee.id.scalar(),
                        employee_name=employee.name.scalar(),
                        alert_type="Leave Usage",
                        alert_reason=f"Employee has only taken {leave_taken} days of leave this year",
                        alert_date=date.today(),
                        alert_severity="Medium",
                        recommended_action="Encourage planned time off",
                    )
                )

            # Check for performance concerns
            performance = (
                db.query(Performance)
                .filter(Performance.employee_id == employee.id)
                .order_by(desc(Performance.review_date))
                .first()
            )
            performance=performance.scalar() if performance else None
            if performance and performance.rating < 3:
                alerts.append(
                    EmployeeAlert(
                        employee_id=employee.id.scalar(),
                        employee_name=employee.name.scalar(),
                        alert_type="Performance",
                        alert_reason=f"Employee has a recent performance rating of {performance.rating}",
                        alert_date=date.today(),
                        alert_severity="Medium",
                        recommended_action="Consider additional training or support",
                    )
                )

        return alerts

    @staticmethod
    def generate_daily_report(
        db: Session, report_date: Optional[date] = None
    ) -> DailyReport:
        """
        Generate a comprehensive daily report on employee well-being
        """
        if not report_date:
            report_date = date.today()

        # Get all active employees count
        total_employees = (
            db.query(func.count(Employee.id))
            .filter(Employee.is_active == True)
            .scalar()
        )

        # Get vibemeter responses for the day
        day_responses = (
            db.query(VibemeterResponse)
            .filter(VibemeterResponse.response_date == report_date)
            .all()
        )

        response_count = len(day_responses)
        response_rate = response_count / total_employees if total_employees else 0

        # Count emotions
        emotion_distribution = {
            "Frustrated": 0,
            "Sad": 0,
            "Okay": 0,
            "Happy": 0,
            "Excited": 0,
        }

        for response in day_responses:
            emotion_distribution[response.emotion_zone] += 1

        # Get escalated sessions for the day
        escalated_sessions = (
            db.query(func.count(ChatSession.id))
            .filter(ChatSession.escalated_to_hr == True)
            .filter(func.date(ChatSession.created_at) == report_date)
            .scalar()
        )

        # Get at-risk employees
        at_risk_alerts = AnalyticsService.identify_at_risk_employees(db)
        at_risk_count = len(at_risk_alerts)

        # Get department breakdown
        departments = db.query(Employee.department).distinct().all()
        department_breakdown = {}

        for dept in departments:
            dept_name = dept[0]
            dept_employees = (
                db.query(func.count(Employee.id))
                .filter(Employee.department == dept_name)
                .filter(Employee.is_active == True)
                .scalar()
            )

            dept_responses = (
                db.query(VibemeterResponse)
                .join(Employee, Employee.id == VibemeterResponse.employee_id)
                .filter(Employee.department == dept_name)
                .filter(VibemeterResponse.response_date == report_date)
                .all()
            )

            dept_emotions = {
                "Frustrated": 0,
                "Sad": 0,
                "Okay": 0,
                "Happy": 0,
                "Excited": 0,
            }

            for response in dept_responses:
                dept_emotions[response.emotion_zone] += 1

            # Calculate sentiment score (higher is better)
            emotion_weights = {
                "Frustrated": 1,
                "Sad": 2,
                "Okay": 3,
                "Happy": 4,
                "Excited": 5,
            }

            sentiment_score = 0
            total_weighted = 0

            for emotion, count in dept_emotions.items():
                sentiment_score += emotion_weights[emotion] * count
                total_weighted += count

            avg_sentiment = sentiment_score / total_weighted if total_weighted else 0

            department_breakdown[dept_name] = {
                "employee_count": dept_employees,
                "response_count": len(dept_responses),
                "response_rate": (
                    len(dept_responses) / dept_employees if dept_employees else 0
                ),
                "emotion_breakdown": dept_emotions,
                "sentiment_score": round(avg_sentiment, 2),
            }

        # Generate recommendations
        recommendations = []

        # Check overall sentiment
        negative_emotions = (
            emotion_distribution["Frustrated"] + emotion_distribution["Sad"]
        )
        negative_ratio = negative_emotions / response_count if response_count else 0

        if negative_ratio > 0.3:
            recommendations.append("Conduct organization-wide well-being initiatives")

        if response_rate < 0.7:
            recommendations.append(
                "Improve Vibemeter participation through reminders and engagement"
            )

        # Add department-specific recommendations
        for dept, data in department_breakdown.items():
            if data["sentiment_score"] < 2.8:
                recommendations.append(f"Address concerns in {dept} department")

        return DailyReport(
            date=report_date,
            total_employees=total_employees,
            response_rate=round(response_rate, 2),
            emotion_distribution=emotion_distribution,
            engagement_metrics={
                "total_responses": response_count,
                "response_rate": round(response_rate, 2),
                "sentiment_score": round(
                    (
                        sum(
                            [
                                1 * emotion_distribution["Frustrated"],
                                2 * emotion_distribution["Sad"],
                                3 * emotion_distribution["Okay"],
                                4 * emotion_distribution["Happy"],
                                5 * emotion_distribution["Excited"],
                            ]
                        )
                        / response_count
                        if response_count
                        else 0
                    ),
                    2,
                ),
            },
            escalated_sessions=escalated_sessions,
            at_risk_employees=at_risk_count,
            support_recommendations=recommendations,
            department_breakdown=department_breakdown,
        )
