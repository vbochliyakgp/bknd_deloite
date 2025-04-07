from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.models.message import MessageSender


class MessageBase(BaseModel):
    sender: MessageSender
    content: str

class MessageCreate(MessageBase):
    chat_session_id: str

class MessageInDBBase(MessageBase):
    id: int
    chat_session_id: str
    timestamp: datetime

    class Config:
        orm_mode = True

class MessageResponse(MessageInDBBase):
    pass


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

class ChatSessionInDBBase(ChatSessionBase):
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        orm_mode = True

class ChatSessionResponse(ChatSessionInDBBase):
    pass

class ChatSessionWithMessages(ChatSessionResponse):
    messages: List[MessageResponse] = []

class ChatNextMessageRequest(BaseModel):
    chat_session_id: str
    message: str


class Message(BaseModel):
    text: str
    audio: Optional[str] = None
    lipsync: Optional[Dict[str, Any]] = None
    facialExpression: str
    animation: str

class ChatResponse(BaseModel):
    messages: List[Message]
