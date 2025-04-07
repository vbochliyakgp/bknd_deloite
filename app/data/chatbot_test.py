#!/usr/bin/env python3

import sys
import os
import argparse
import json
from pydantic import BaseModel, create_model, Field, ValidationError
from openai import OpenAI
import pytz
from datetime import datetime

# Initialize the OpenAI client (ensure your API key is set in the environment)
client = OpenAI()

# Define the TIA system prompt using the template from paste-2.txt
system_prompt = """
You are an empathetic AI assistant named "TIA" working in Deloitte's People Experience team. Your role is to analyze employee data, identify potential concerns, and have meaningful conversations with employees to understand their well-being and provide appropriate suggestions.

IMPORTANT: Keep your responses short, conversational and human-like. Only ask ONE question at a time. Do not have a conversation with yourself.

CONTEXT:
You have access to the following data for employee {employee_id}:

1. VIBEMETER DATA:
- Response Date: {vibe_date}
- Vibe Score: {vibe_score}/5
- Emotion Zone: {emotion_zone}

2. LEAVE DATA:
- Leave Type: {leave_type}
- Leave Days Taken (Year to Date): {leave_days_taken}
- Last Leave Start Date: {leave_start_date}
- Last Leave End Date: {leave_end_date}

3. ACTIVITY TRACKER:
- Average Teams Messages Sent (Last 30 Days): {avg_teams_messages}
- Average Emails Sent (Last 30 Days): {avg_emails}
- Average Meetings Attended (Last 30 Days): {avg_meetings}
- Average Work Hours (Last 30 Days): {avg_work_hours}

4. PERFORMANCE DATA:
- Review Period: {review_period}
- Performance Rating: {performance_rating}/5
- Manager Feedback Summary: {manager_feedback}
- Promotion Consideration: {promotion_flag}

5. REWARDS & RECOGNITION:
- Latest Award Type: {latest_award_type}
- Latest Award Date: {latest_award_date}
- Reward Points (Year to Date): {reward_points}

6. ONBOARDING EXPERIENCE:
- Joining Date: {joining_date}
- Onboarding Feedback: {onboarding_feedback}
- Mentor Assigned: {mentor_assigned}
- Initial Training Completed: {training_completed}

REFERENCE THRESHOLDS:
{{"thresholds": {{
    "vibe": {{
        "concerningScore": 2,
        "criticalScore": 1,
        "targetEmotionZones": [
            "Frustrated Zone",
            "Sad Zone",
            "Leaning to Sad Zone"
        ]
    }},
    "workActivity": {{
        "hours": {{
            "concerning": 8.6,
            "critical": 9.3
        }},
        "meetings": {{
            "healthy": 4,
            "concerning": 7
        }}
    }},
    "leave": {{
        "insufficient": 6,
        "healthy": 11
    }},
    "performance": {{
        "concerning": 1,
        "promotion": 3
    }},
    "rewards": {{
        "insufficient": 183,
        "quarterly": 96
    }},
    "riskScore": {{
        "weights": {{
            "vibe": 0.4,
            "workHours": 0.15,
            "meetings": 0.15,
            "leave": 0.15,
            "performance": 0.1,
            "rewards": 0.05
        }},
        "levels": {{
            "low": {{ "min": 0, "max": 3.9 }},
            "medium": {{ "min": 4, "max": 6.9 }},
            "high": {{ "min": 7, "max": 10 }}
        }},
        "escalationThreshold": 7
    }}
}}}}

YOUR TASK:
1. Based on the data above, identify potential areas of concern for this employee
2. Have a conversation with the employee to understand their well-being
3. Ask relevant questions based on the data patterns
4. Provide personalized suggestions
5. Calculate a risk score based on their vibe, responses, and overall data
6. Return a structured response

CONVERSATION FLOW:
1. Introduce yourself briefly only once at the start
2. Express interest in the employee's well-being with short, human-like responses
3. Ask ONE specific question at a time based on their data patterns and responses
4. Listen to their feedback
5. Provide brief, supportive suggestions
6. Thank them for their time

IMPORTANT:
1. Keep responses concise - aim for 1-3 sentences per response
2. Sound natural and conversational, not corporate or scripted
3. Only ask ONE question per response
4. ROTATE QUESTIONS from different domains - don't ask multiple questions about the same topic
5. Ensure coverage of all data categories (vibemeter, activity, leave, performance, rewards, onboarding)
6. Be responsive to what the employee actually says - don't ask unrelated questions
7. Don't repeat previous questions
8. If you've asked about one domain (e.g., work hours), move to a different domain in your next question (e.g., leave balance or performance)

QUESTION BANK (use where relevant):
- How have you been feeling at work lately? (based on Vibe_Score, Emotion_Zone)
- What aspects of your work environment would you like to see improved? (general well-being)
- Is there anything specific causing you stress or frustration? (for low Vibe_Score)
- How do you feel about your current workload? (based on Work_Hours, Meetings_Attended)
- Have you been able to take enough time off to recharge? (based on Leave_Days)
- Do you feel your recent performance review was fair? (based on Performance_Rating)
- How helpful was the feedback from your manager? (based on Manager_Feedback)
- Do you feel recognized for your contributions? (based on Award_Type, Reward_Points)
- How was your onboarding experience with us? (for newer employees, based on Onboarding_Feedback)
- Was your assigned mentor helpful during your initial period? (based on Mentor_Assigned)
- Do you feel you have the right tools and training to succeed? (based on Initial_Training_Completed)
- Would you like more opportunities for growth or skill development? (based on Promotion_Consideration)

RISK SCORE CALCULATION:
1. Start with a base score of 0
2. Add points based on different factors:
   - Vibe Score: Add 3 points if ≤ 1 (criticalScore), 2 points if ≤ 2 (concerningScore)
   - Emotion Zone: Add 2 points if in ["Frustrated Zone", "Sad Zone", "Leaning to Sad Zone"]
   - Work Hours: Add 2 points if ≥ 9.3 (critical), 1 point if ≥ 8.6 (concerning)
   - Meeting Load: Add 1 point if ≥ 7 (concerning)
   - Leave Usage: Add 1 point if ≤ 6 days (insufficient)
   - Performance: Add 2 points if ≤ 1 (concerning)
   - Rewards: Add 0.5 points if points ≤ 183 (insufficient)
3. Add 1-3 points based on the content of their responses (subjective assessment)
4. Set isComplete to true after collecting enough information (typically after 2-3 exchanges)
5. Maximum score is 10
6. HR escalation threshold is 7 - recommend escalation if score is ≥ 7

OUTPUT STRUCTURE:
Your response should include:
1. Your conversation with the employee
2. A risk score (0-10)
3. List of key risk factors identified
4. Personalized suggestions
5. Whether HR escalation is recommended (true if risk score ≥ escalationThreshold)
6. Whether the conversation is complete (true/false)
"""

# Create a new Pydantic model for the TIA response format
class TIAResponse(BaseModel):
    reply: str = Field(..., description="Conversation with the employee, including questions and responses")
    risk_score: float = Field(..., description="Risk score (0-10)")
    risk_factors: list[str] = Field(..., description="List of key risk factors identified")
    suggestions: list[str] = Field(..., description="List of personalized suggestions for the employee")
    hr_escalation: bool = Field(..., description="Whether HR escalation is recommended")
    isComplete: bool = Field(..., description="Whether the conversation is complete")

# Sample employee data (in a real scenario, these would come from a database)
def get_dummy_employee_data():
    # Sample employee data
    employee_data = {
        "id": "EMP12345",
        "name": "Jane Smith",
        "department": "Marketing",
        "position": "Marketing Specialist"
    }
    
    vibe_data = {
        "date": "2025-04-01",
        "score": 2,
        "zone": "Frustrated Zone"
    }
    
    leave_data = {
        "type": "Annual",
        "days_taken": 5,
        "start_date": "2025-03-10",
        "end_date": "2025-03-14"
    }
    
    activity_data = {
        "avg_teams_messages": 25,
        "avg_emails": 30,
        "avg_meetings": 8,
        "avg_work_hours": 9.5
    }
    
    performance_data = {
        "review_period": "Q1 2025",
        "rating": 3,
        "feedback": "Jane is meeting expectations but could improve time management",
        "promotion_flag": "Not eligible"
    }
    
    rewards_data = {
        "latest_award_type": "Team Player",
        "latest_award_date": "2024-12-15",
        "points": 120
    }
    
    onboarding_data = {
        "joining_date": "2024-06-01",
        "feedback": "Satisfactory",
        "mentor_assigned": "Yes",
        "training_completed": "Yes"
    }
    
    # Based on problem statement dataset columns
    # Mapping the data to match the expected column names
    mapped_data = {
        "employee_data": {
            "id": employee_data["id"],
            "name": employee_data["name"],
            "department": employee_data["department"],
            "position": employee_data["position"]
        },
        "vibe_data": {
            "date": vibe_data["date"],
            "score": vibe_data["score"],
            "zone": vibe_data["zone"]
        },
        "leave_data": {
            "type": leave_data["type"],
            "days_taken": leave_data["days_taken"],
            "start_date": leave_data["start_date"],
            "end_date": leave_data["end_date"]
        },
        "activity_data": {
            "avg_teams_messages": activity_data["avg_teams_messages"],
            "avg_emails": activity_data["avg_emails"],
            "avg_meetings": activity_data["avg_meetings"],
            "avg_work_hours": activity_data["avg_work_hours"]
        },
        "performance_data": {
            "review_period": performance_data["review_period"],
            "rating": performance_data["rating"],
            "feedback": performance_data["feedback"],
            "promotion_flag": performance_data["promotion_flag"]
        },
        "rewards_data": {
            "latest_award_type": rewards_data["latest_award_type"],
            "latest_award_date": rewards_data["latest_award_date"],
            "points": rewards_data["points"]
        },
        "onboarding_data": {
            "joining_date": onboarding_data["joining_date"],
            "feedback": onboarding_data["feedback"],
            "mentor_assigned": onboarding_data["mentor_assigned"],
            "training_completed": onboarding_data["training_completed"]
        }
    }
    
    return mapped_data

def format_system_prompt(data):
    # Fill in the system prompt template with the actual employee data
    employee = data['employee_data']
    vibe = data['vibe_data']
    leave = data['leave_data']
    activity = data['activity_data']
    performance = data['performance_data']
    rewards = data['rewards_data']
    onboarding = data['onboarding_data']
    
    formatted_prompt = system_prompt.format(
        employee_id=employee['id'],
        vibe_date=vibe['date'],
        vibe_score=vibe['score'],
        emotion_zone=vibe['zone'],
        leave_type=leave['type'],
        leave_days_taken=leave['days_taken'],
        leave_start_date=leave['start_date'],
        leave_end_date=leave['end_date'],
        avg_teams_messages=activity['avg_teams_messages'],
        avg_emails=activity['avg_emails'],
        avg_meetings=activity['avg_meetings'],
        avg_work_hours=activity['avg_work_hours'],
        review_period=performance['review_period'],
        performance_rating=performance['rating'],
        manager_feedback=performance['feedback'],
        promotion_flag=performance['promotion_flag'],
        latest_award_type=rewards['latest_award_type'],
        latest_award_date=rewards['latest_award_date'],
        reward_points=rewards['points'],
        joining_date=onboarding['joining_date'],
        onboarding_feedback=onboarding['feedback'],
        mentor_assigned=onboarding['mentor_assigned'],
        training_completed=onboarding['training_completed']
    )
    return formatted_prompt

def chat_with_user():
    # Get dummy employee data
    employee_data = get_dummy_employee_data()
    
    # Format the system prompt with employee data
    formatted_system_prompt = format_system_prompt(employee_data)
    
    # Initialize conversation history with the system prompt
    chat_history = [{"role": "system", "content": formatted_system_prompt}]
    
    print(f"TIA - Deloitte Employee Wellness Assistant")
    print(f"Analyzing data for employee: {employee_data['employee_data']['name']} (ID: {employee_data['employee_data']['id']})")
    print("Type 'bye' to exit.\n")
    print("You can also type 'temp=X' (where X is a value between 0 and 2) to change the temperature setting.")
    
    # Default temperature
    temperature = 0.7
    print(f"Current temperature setting: {temperature}")
    
    # Hardcoded first response
    first_response = {
        "reply": "Hi, I'm TIA. I noticed your recent feedback shows you might be feeling frustrated at work. What's your biggest challenge right now?",
        "risk_score": 5.0,
        "risk_factors": ["Vibe Score in Frustrated Zone"],
        "suggestions": ["Listen to employee concerns"],
        "hr_escalation": False,
        "isComplete": False
    }
    
    # Display the hardcoded first response
    print("TIA:", first_response["reply"])
    
    # Add the hardcoded first response to the chat history
    chat_history.append({"role": "assistant", "content": json.dumps(first_response)})
    
    # Conversation counter and completion tracking
    message_count = 1
    has_risk_info = False
    
    # Track which domains we've covered to ensure diversity
    domains_covered = {
        "vibe": True,  # First question is already about vibe
        "work_activity": False,
        "leave": False,
        "performance": False,
        "rewards": False,
        "onboarding": False
    }
    
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ["bye", "exit"]:
            print("TIA: Thank you for your time! Have a great day!")
            break
            
        # Check if user wants to change temperature
        if user_input.lower().startswith("temp="):
            try:
                new_temp = float(user_input.split("=")[1].strip())
                if 0 <= new_temp <= 2:
                    temperature = new_temp
                    print(f"Temperature changed to: {temperature}")
                else:
                    print("Temperature must be between 0 and 2")
                continue
            except ValueError:
                print("Invalid temperature format. Use 'temp=X' where X is a number between 0 and 2")
                continue
        
        # Append user input to chat history
        chat_history.append({"role": "user", "content": user_input})
        
        # Increment message count
        message_count += 1
        
        # Add system instruction to guide domain selection
        domains_not_covered = [domain for domain, covered in domains_covered.items() if not covered]
        if domains_not_covered:
            prioritize_domain = domains_not_covered[0]
            domain_instruction = f"For your next question, please focus on the {prioritize_domain.replace('_', ' ')} domain that we haven't covered yet. After this response, mark this domain as covered."
            chat_history.append({"role": "system", "content": domain_instruction})
       
        try:
            print(f"Generating response with temperature: {temperature}")
            
            # Start timing
            import time
            start_time = time.time()
            
            response = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=chat_history,
                temperature=temperature,
                response_format=TIAResponse
            )
            
            # End timing and calculate elapsed time in milliseconds
            elapsed_time_ms = (time.time() - start_time) * 1000
            
            # Remove the temporary system instruction if we added it
            if domains_not_covered:
                chat_history.pop()  # Remove the domain instruction
            
            assistant_reply = response.choices[0].message.content.strip()
           
            try:
                parsed = json.loads(assistant_reply)
                
                # Convert string booleans to actual booleans if necessary
                boolean_fields = ['hr_escalation', 'isComplete']
                for field in boolean_fields:
                    if field in parsed and isinstance(parsed[field], str):
                        parsed[field] = parsed[field].lower() == 'true'
                
                # Check if we've gathered some risk information or have had enough exchanges
                if parsed.get('risk_score', 0) > 0 and len(parsed.get('risk_factors', [])) > 0:
                    has_risk_info = True
                
                # Mark the prioritized domain as covered
                if domains_not_covered:
                    domains_covered[prioritize_domain] = True
                
                # Set isComplete to true after covering most domains or having 4+ messages
                if message_count >= 4 or (has_risk_info and sum(domains_covered.values()) >= 4):
                    parsed['isComplete'] = True
                
                # Validate and parse using the Pydantic model
                output = TIAResponse(**parsed)                
                print("\n -----------------------")
                print("Current State of TIA Response:")
                print(output.model_dump_json(indent=4))
                print(f"Generated with temperature: {temperature}")
                print(f"Response time: {elapsed_time_ms:.2f} ms")
                print(f"Message count: {message_count}")
                print(f"Domains covered: {[domain for domain, covered in domains_covered.items() if covered]}")
                print(f"Has risk info: {has_risk_info}")
                print(f"Is complete: {output.isComplete}")
                print("\n -----------------------")

                # Just print the conversation part to the user
                print("TIA:", output.reply)

            except Exception as parse_err:
                print("TIA (raw):", assistant_reply)
                print(f"Error parsing response: {parse_err}")
                print(f"Response time: {elapsed_time_ms:.2f} ms")
                
            # Append the assistant's reply to history
            chat_history.append({"role": "assistant", "content": assistant_reply})
            
        except Exception as e:
            print(f"[ERROR] OpenAI API call failed: {e}")
            continue

if __name__ == "__main__":
    chat_with_user()