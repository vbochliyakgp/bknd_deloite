# app/api/chatbot.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.dependencies import get_db, get_current_employee
from app.models.employee import Employee
from app.models.chat_session import ChatSession, SessionStatus
from app.models.message import Message, MessageSender
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionWithMessages,
    MessageCreate,
    MessageResponse,
    ChatNextMessageRequest,
    ChatNextMessageResponse,
)
from app.core.openai_client import openai_client
from app.services.analytics import AnalyticsService
from app.services.email import EmailService

router = APIRouter()


@router.post(
    "/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED
)
async def create_chat_session(
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """
    Create a new chat session for the employee
    """
    # Check if there's already an active session
    active_session = (
        db.query(ChatSession)
        .filter(
            ChatSession.employee_id == current_employee.id,
            ChatSession.session_status == SessionStatus.ACTIVE,
        )
        .first()
    )

    if active_session:
        return active_session

    # Create new session
    new_session = ChatSession(
        employee_id=current_employee.id, session_status=SessionStatus.ACTIVE
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Add welcome message
    welcome_message = Message(
        chat_session_id=new_session.id,
        sender=MessageSender.BOT,
        content=f"Hello {current_employee.name}! How are you feeling today? I'm here to chat and help with any concerns you might have.",
    )

    db.add(welcome_message)
    db.commit()

    return new_session


@router.get("/sessions/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """
    Get a chat session with messages
    """
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id, ChatSession.employee_id == current_employee.id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    messages = (
        db.query(Message)
        .filter(Message.chat_session_id == session_id)
        .order_by(Message.timestamp)
        .all()
    )
    message_responses = [MessageResponse.from_orm(message) for message in messages]

    return ChatSessionWithMessages(**session.__dict__, messages=message_responses)


@router.get("/sessions/active", response_model=Optional[ChatSessionWithMessages])
async def get_active_session(
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """
    Get the active chat session for the employee
    """
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.employee_id == current_employee.id,
            ChatSession.session_status == SessionStatus.ACTIVE,
        )
        .first()
    )

    if not session:
        return None

    messages = (
        db.query(Message)
        .filter(Message.chat_session_id == session.id)
        .order_by(Message.timestamp)
        .all()
    )
    message_responses = [MessageResponse.from_orm(message) for message in messages]
    return ChatSessionWithMessages(**session.__dict__, messages=message_responses)


@router.post("/sessions/{session_id}/messages", response_model=ChatNextMessageResponse)
async def send_message(
    session_id: int,
    request: ChatNextMessageRequest,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """
    Send a message and get AI response
    """
    # Verify session exists and belongs to the employee
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.employee_id == current_employee.id,
            ChatSession.session_status == SessionStatus.ACTIVE,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active chat session not found",
        )

    # Add user message to DB
    user_message = Message(
        chat_session_id=session_id,
        sender=MessageSender.EMPLOYEE,
        content=request.message,
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # Get previous messages for context
    previous_messages = (
        db.query(Message)
        .filter(Message.chat_session_id == session_id)
        .order_by(Message.timestamp)
        .all()
    )

    previous_messages_formatted = [
        {"sender": msg.sender, "content": msg.content, "timestamp": msg.timestamp}
        for msg in previous_messages
    ]

    # Get employee data for context
    employee_data = AnalyticsService.get_employee_data(db, current_employee.id.scalar())

    # Generate AI response
    ai_response = await openai_client.generate_response(
        db=db,
        employee_id=current_employee.id.scalar(),
        chat_session_id=session_id,
        message=request.message,
        previous_messages=previous_messages_formatted,
        employee_data=employee_data,
    )

    # Save AI response to DB
    bot_message = Message(
        chat_session_id=session_id,
        sender=MessageSender.BOT,
        content=ai_response["content"],
    )

    db.add(bot_message)

    # Check if session needs to be escalated
    if ai_response["escalation_recommended"]:
        session.escalated_to_hr = True
        session.escalation_reason = ai_response["escalation_reason"]

        # Notify HR about escalation
        await EmailService.send_hr_notification(
            employee_name=str(current_employee.name),
            session_id=session_id,
            reason=ai_response["escalation_reason"],
        )

    db.commit()
    db.refresh(bot_message)

    return ChatNextMessageResponse(
        message=bot_message,
        suggested_replies=ai_response["suggested_replies"],
        escalation_recommended=ai_response["escalation_recommended"],
    )


@router.post("/sessions/{session_id}/end", response_model=ChatSessionResponse)
async def end_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """
    End a chat session
    """
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.employee_id == current_employee.id,
            ChatSession.session_status == SessionStatus.ACTIVE,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active chat session not found",
        )

    session.update(session_status = SessionStatus.COMPLETED)
    session.update(end_time = datetime.now())

    # Add farewell message
    farewell_message = Message(
        chat_session_id=session_id,
        sender=MessageSender.BOT,
        content="Thank you for chatting with me today! I hope our conversation was helpful. Have a great day!",
    )

    db.add(farewell_message)
    db.commit()
    db.refresh(session)

    return session
