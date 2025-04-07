# app/schemas/upload.py
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class DatasetType(str, Enum):
    LEAVE = "leave"
    ACTIVITY = "activity"
    REWARDS = "rewards"
    PERFORMANCE = "performance"
    ONBOARDING = "onboarding"
    VIBEMETER = "vibemeter"


class AtRiskEmployee(BaseModel):
    employee_id: str


class UploadResponse(BaseModel):
    at_risk_employees: Optional[list[AtRiskEmployee]] = None
