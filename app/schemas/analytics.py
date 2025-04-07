# app/schemas/analytics.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import date


class EmployeeAlert(BaseModel):
    employee_id: int
    employee_name: str
    alert_type: str
    alert_reason: str
    alert_date: date
    alert_severity: str
    recommended_action: str


class EmployeeSessionAnalyticsNew(BaseModel):
    employee_id: str
    session_id: int
    escalated: bool
    summary: str
    suggestions: str
    risk_score: int
    start_time: date
    end_time: date


class EmployeeSessionAnalytics(BaseModel):
    employee_id: int
    employee_name: str
    session_count: int
    average_session_length: float  # in minutes
    most_common_emotion: str
    emotion_trend: List[Dict[str, Any]]
    leave_usage: Dict[str, Any]
    activity_metrics: Dict[str, Any]
    performance_data: Dict[str, Any]
    rewards_data: Dict[str, Any]
    risk_factors: List[str]
    recommended_actions: List[str]


class DailyReport(BaseModel):
    date: date
    total_employees: int
    response_rate: float
    emotion_distribution: Dict[str, int]
    engagement_metrics: Dict[str, Any]
    escalated_sessions: int
    at_risk_employees: int
    support_recommendations: List[str]
    department_breakdown: Dict[str, Dict[str, Any]]
