# app/schemas/dashboard.py

from pydantic import BaseModel, RootModel
from typing import List, Dict, Any, Optional

class VibeStats(BaseModel):
    percentage: float
    count: int

class AttentionStats(BaseModel):
    count: int
    percentage: float

class ConversationStats(BaseModel):
    total: int
    needing_attention: int

class TrendPoint(BaseModel):
    date: str
    score: float

class VibemeterTrendData(RootModel):
    root: List[TrendPoint]

class VibeDistribution(BaseModel):
    categories: List[str]
    counts: List[int]
    percentages: List[int]
    total_responses: int

class DashboardResponse(BaseModel):
    positive_vibes: VibeStats
    negative_vibes: VibeStats
    employees_needing_attention: AttentionStats
    ai_conversations: ConversationStats
    vibemeter_trend: List[TrendPoint]
    vibe_distribution: VibeDistribution

    class Config:
        schema_extra = {
            "example": {
                "positive_vibes": {
                    "percentage": 60.0,
                    "count": 180
                },
                "negative_vibes": {
                    "percentage": 40.0,
                    "count": 120
                },
                "employees_needing_attention": {
                    "count": 10,
                    "percentage": 100.0
                },
                "ai_conversations": {
                    "total": 60,
                    "needing_attention": 14
                },
                "vibemeter_trend": [
                    {"date": "Mar 9", "score": 8.5},
                    {"date": "Mar 10", "score": 7.2},
                    # ... more data points
                ],
                "vibe_distribution": {
                    "categories": ["Critical", "Concerned", "Neutral", "Happy", "Very Happy"],
                    "counts": [27, 38, 24, 30, 32],
                    "percentages": [18, 25, 16, 20, 21],
                    "total_responses": 153
                }
            }
        }