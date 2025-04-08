# app/api/chatbot.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import os
from typing import List
import random

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
    # Check if employee can start a chat session
    if current_employee.wellness_check_status != "not_received":
        raise HTTPException(
            status_code=403, 
            detail="Employee has either completed the chat or is not authorized to chat"
        )
    print("Chat session creation initiated")
    # Verify the employee ID in the request matches the authenticated employee
    if chat_session.employee_id != current_employee.id:
        raise HTTPException(
            status_code=403,
            detail="Employee ID in request does not match authenticated employee"
        )

    # Check for existing active session
    existing_session = db.query(ChatSession).filter(
        ChatSession.employee_id == current_employee.id,
        ChatSession.session_id == chat_session.session_id,
    ).first()
    
    if existing_session:
        return existing_session

    # Create new session
    print("Creating new chat session")
    new_session = ChatSession(**chat_session.dict())
    
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

@router.post("/sessions/{session_id}/message")
async def send_message(
    session_id: str,
    msg: MessageCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    print(f"Received message for session_id: {session_id}, from employee: {current_employee.id}")
    
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.employee_id == current_employee.id
    ).first()
    if not session:
        print(f"Session not found for session_id: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    print("Session found, saving user message")
    # Save the user message
    user_msg = Message(session_id=session_id, question=msg.question, answer="")
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    print(f"User message saved: {user_msg.question}")
    
    # Get employee data
    print(f"Fetching employee data for employee_id: {current_employee.id}")
    employee_data = AnalyticsService.get_employee_data(db, current_employee.id)
    print(f"Employee data fetched: {employee_data}")
    
    # Get message history for context
    print(f"Fetching message history for session_id: {session_id}")
    history = db.query(Message).filter(Message.session_id == session_id).all()
    prev_messages = [
        {"question": m.question, "answer": m.answer} for m in history
    ]
    print(f"Message history: {prev_messages}")
    
    # Call AI with history
    print("Calling AI to generate response")
    ai_response = await openai_client.generate_response(
        db=db,
        employee_id=current_employee.id,
        chat_session_id=session_id,
        message=msg.question,
        previous_messages=prev_messages,
        employee_data=employee_data,
    )
    print(f"AI response received: {ai_response}")
    
    # Create and save the bot message
    bot_msg = Message(
        session_id=session_id,
        question="",
        answer=ai_response["content"][0]["text"]
    )
    db.add(bot_msg)
    print(f"Bot message created: {bot_msg.answer}")
    
    # Update session data if conversation is complete
    if ai_response.get("isComplete", False):
        print("Conversation marked as complete, updating session data")
        session.risk_factors = ", ".join(ai_response.get("risk_factors", []))
        session.risk_score = ai_response.get("risk_score", 0)
        session.suggestions = ", ".join(ai_response.get("suggestions", []))
    
    # Handle escalation recommendation
    if ai_response.get("hr_escalation", False):
        print("HR escalation recommended, sending notification")
        session.escalated = True
        await EmailService.send_hr_notification(
            employee_name=str(current_employee.name),
            session_id=session_id,
            reason=session.suggestions,
        )
    
    i=random.randint(1000,9999)
    mp3_filename = f"message_{i}.mp3"
    mp3_path = os.path.join(settings.AUDIO_DIR, mp3_filename)
    await elevenlabs_service.text_to_speech(bot_msg.answer, mp3_filename)
    
    # Process audio (convert to WAV, generate lipsync)
    audio_base64, lipsync_data = await audio_service.process_audio_for_message(i, bot_msg.answer)
    
    # Create message object
    message = {
        "text": bot_msg.answer,
        "audio": audio_base64,
        "lipsync": lipsync_data,
        "facialExpression": 'message_data["facialExpression"]',
        "animation": 'message_data["animation"]'
    }



    db.commit()
    db.refresh(bot_msg)
    print("Database changes committed and bot message refreshed")

    return [message]

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