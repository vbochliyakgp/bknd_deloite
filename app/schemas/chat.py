# app/schemas/chat.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    question: str
    answer: str

class MessageCreate(MessageBase):
    session_id: str

class MessageResponse(MessageBase):
    id: int
    session_id: str

    class Config:
        orm_mode = True

class ChatSessionBase(BaseModel):
    employee_id: str
    summary: Optional[str] = None
    escalated: bool = False
    suggestions: Optional[str] = None
    risk_score: Optional[int] = None

class ChatSessionCreate(ChatSessionBase):
    session_id: str

class ChatSessionUpdate(BaseModel):
    summary: Optional[str] = None
    escalated: Optional[bool] = None
    suggestions: Optional[str] = None
    risk_score: Optional[int] = None
    end_time: Optional[datetime] = None

class ChatSessionResponse(ChatSessionBase):
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        orm_mode = True

class ChatSessionWithMessages(ChatSessionResponse):
    messages: List[MessageResponse]
