
# app/schemas/chat.py
from typing import Optional, List,Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.models.chat_session import SessionStatus
from app.models.message import MessageSender


class MessageBase(BaseModel):
    sender: MessageSender
    content: str

class MessageCreate(MessageBase):
    chat_session_id: int

class MessageInDBBase(MessageBase):
    id: int
    chat_session_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class MessageResponse(MessageInDBBase):
    pass

class ChatSessionBase(BaseModel):
    employee_id: int
    session_status: SessionStatus = SessionStatus.ACTIVE
    summary: Optional[str] = None
    escalated_to_hr: bool = False
    escalation_reason: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseModel):
    session_status: Optional[SessionStatus] = None
    summary: Optional[str] = None
    escalated_to_hr: Optional[bool] = None
    escalation_reason: Optional[str] = None
    end_time: Optional[datetime] = None

class ChatSessionInDBBase(ChatSessionBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ChatSessionResponse(ChatSessionInDBBase):
    pass

class ChatSessionWithMessages(ChatSessionResponse):
    messages: List[MessageResponse] = []

class ChatNextMessageRequest(BaseModel):
    chat_session_id: int
    message: str


class Message(BaseModel):
    text: str
    audio: Optional[str] = None
    lipsync: Optional[Dict[str, Any]] = None
    facialExpression: str
    animation: str

class ChatResponse(BaseModel):
    messages: List[Message]
