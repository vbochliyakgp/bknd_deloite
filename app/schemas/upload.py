
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

class UploadResponse(BaseModel):
    filename: str
    dataset_type: DatasetType
    rows_processed: int
    success: bool
    message: str