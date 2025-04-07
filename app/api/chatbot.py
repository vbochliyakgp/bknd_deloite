# app/api/chatbot.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import os
from typing import List

from app.dependencies import get_db, get_current_employee
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.models.employee import Employee
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionWithMessages,
    ChatSessionUpdate,
    MessageCreate,
    MessageResponse
)
from app.services.analytics import AnalyticsService
from app.services.email import EmailService
from app.services.audio_service import audio_service
from app.services.elevenlabs_service import elevenlabs_service
from app.core.openai_client import openai_client
from app.config import settings

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    chat_session: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    existing_session = db.query(ChatSession).filter(
        ChatSession.employee_id == current_employee.id,
        ChatSession.session_id == chat_session.session_id
    ).first()
    if existing_session:
        return existing_session

    new_session = ChatSession(**chat_session.dict(), employee_id=current_employee.id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/sessions/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.employee_id == current_employee.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = db.query(Message).filter(Message.session_id == session_id).all()
    return ChatSessionWithMessages(
        **session.__dict__,
        messages=[MessageResponse.from_orm(m) for m in messages]
    )

@router.post("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def send_message(
    session_id: str,
    msg: MessageCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.employee_id == current_employee.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_msg = Message(session_id=session_id, question=msg.question, answer="")
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    history = db.query(Message).filter(Message.session_id == session_id).all()
    prev_messages = [
        {"question": m.question, "answer": m.answer} for m in history
    ]

    employee_data = AnalyticsService.get_employee_data(db, current_employee.id)
    ai_response = await openai_client.generate_response(
        db=db,
        employee_id=current_employee.id,
        chat_session_id=session_id,
        message=msg.question,
        previous_messages=prev_messages,
        employee_data=employee_data,
    )

    bot_msg = Message(
        session_id=session_id,
        question=msg.question,
        answer=ai_response["content"][0]["text"]
    )
    db.add(bot_msg)

    if ai_response.get("escalation_recommended"):
        session.escalated = True
        session.suggestions = ai_response.get("escalation_reason")
        await EmailService.send_hr_notification(
            employee_name=str(current_employee.name),
            session_id=session_id,
            reason=session.suggestions,
        )

    db.commit()
    db.refresh(bot_msg)

    return [
        MessageResponse.from_orm(user_msg),
        MessageResponse.from_orm(bot_msg)
    ]

@router.post("/sessions/{session_id}/end", response_model=ChatSessionResponse)
async def end_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.employee_id == current_employee.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    session.end_time = datetime.utcnow()

    farewell_message = Message(
        session_id=session_id,
        question="Session Ended",
        answer="Thank you for chatting with me today! I hope our conversation was helpful."
    )

    db.add(farewell_message)
    db.commit()
    db.refresh(session)

    return session
