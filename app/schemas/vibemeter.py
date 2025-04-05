
# app/schemas/vibemeter.py
from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime
from app.models.vibemeter import EmotionZone

class VibemeterResponseBase(BaseModel):
    employee_id: int
    emotion_zone: EmotionZone
    comment: Optional[str] = None

class VibemeterResponseCreate(VibemeterResponseBase):
    response_date: Optional[date] = None

class VibemeterResponseInDBBase(VibemeterResponseBase):
    id: int
    response_date: date
    created_at: datetime

    class Config:
        orm_mode = True

class VibemeterResponseResponse(VibemeterResponseInDBBase):
    pass

class VibemeterAnalytics(BaseModel):
    employee_count: int
    frustrated_count: int
    sad_count: int
    okay_count: int
    happy_count: int
    excited_count: int
    date: date
