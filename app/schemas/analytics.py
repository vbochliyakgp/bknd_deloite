# app/schemas/analytics.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
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


class ExecutiveSummary(BaseModel):
    total_employees_analyzed: int
    employees_requiring_followup: int
    conversations_conducted: int
    hr_intervention_cases: int


class RiskCategory(BaseModel):
    category: str
    count: int
    percentage: float
    change_from_previous: str
    top_emotion_zone: str


class KeyMetrics(BaseModel):
    risk_categories: List[RiskCategory]


class KeyInsight(BaseModel):
    insight: str
    percentage: float
    change: str


class RiskFactor(BaseModel):
    factor: str
    count: int
    percentage: float


class DepartmentAnalysis(BaseModel):
    department: str
    avg_vibe_score: float
    high_risk_percentage: float
    key_risk_factor: str


class ConversationInsights(BaseModel):
    common_themes: List[str]
    employee_quotes: List[str]


class FocusArea(BaseModel):
    area: str
    actions: List[str]


class ActionItem(BaseModel):
    item: str
    timeline: str
    owner: str


class SuccessStory(BaseModel):
    title: str
    impact: str
    improvement: str


class HighRiskEmployee(BaseModel):
    employee_id: str
    risk_score: int
    primary_concerns: List[str]
    recommended_actions: List[str]
    requires_immediate_attention: bool


class DailyReport(BaseModel):
    report_date: date
    report_title: str = "Deloitte People Experience Daily Report"
    executive_summary: ExecutiveSummary
    key_metrics: KeyMetrics
    key_insights: List[KeyInsight]
    top_risk_factors: List[RiskFactor]
    department_analysis: List[DepartmentAnalysis]
    conversation_insights: ConversationInsights
    recommended_focus_areas: List[FocusArea]
    immediate_action_items: List[ActionItem]
    success_stories: List[SuccessStory]
    high_risk_employees: List[HighRiskEmployee]

    class Config:
        json_schema_extra = {
            "example": {
                "report_date": "2025-04-07",
                "report_title": "Deloitte People Experience Daily Report",
                "executive_summary": {
                    "total_employees_analyzed": 150,
                    "employees_requiring_followup": 23,
                    "conversations_conducted": 150,
                    "hr_intervention_cases": 8,
                },
                "key_metrics": {
                    "risk_categories": [
                        {
                            "category": "High Risk (7-10)",
                            "count": 15,
                            "percentage": 10,
                            "change_from_previous": "+2%",
                            "top_emotion_zone": "Stress",
                        },
                        {
                            "category": "Medium Risk (4-6)",
                            "count": 45,
                            "percentage": 30,
                            "change_from_previous": "-5%",
                            "top_emotion_zone": "Concern",
                        },
                        {
                            "category": "Low Risk (1-3)",
                            "count": 90,
                            "percentage": 60,
                            "change_from_previous": "+3%",
                            "top_emotion_zone": "Satisfaction",
                        },
                    ]
                },
                "key_insights": [
                    {
                        "insight": "Work-life balance concerns are increasing in the Engineering department",
                        "percentage": 24,
                        "change": "+5%",
                    }
                ],
            }
        }
