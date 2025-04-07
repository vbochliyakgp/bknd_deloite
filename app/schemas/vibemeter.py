# app/schemas/vibemeter.py
from typing import Optional
from pydantic import BaseModel
from datetime import date, datetime


class VibemeterAnalytics(BaseModel):
    employee_count: int
    frustrated_count: int
    sad_count: int
    okay_count: int
    happy_count: int
    excited_count: int
    date: date
