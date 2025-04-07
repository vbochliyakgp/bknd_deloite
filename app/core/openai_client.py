# app/core/openai_client.py
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from app.config import settings
# from app.models.message import MessageSender
from sqlalchemy.orm import Session
import json
import logging
from openai.types.chat import ChatCompletionMessageParam

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_response(
        self,
        db: Session,
        employee_id: int,
        chat_session_id: int,
        message: str,
        previous_messages: List[Dict[str, Any]],
        employee_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a response using OpenAI's API with employee context
        """
        try:
            # Format previous messages for OpenAI
            formatted_messages: List[ChatCompletionMessageParam] = [
                {"role": "system", "content": self._create_system_prompt(employee_data)}
            ]

            # Add previous messages
            for prev_msg in previous_messages:
                if prev_msg["sender"] == 0:
                    formatted_messages.append(
                        {"role": "assistant", "content": prev_msg["content"]}
                    )
                else:
                    formatted_messages.append(
                        {"role": "user", "content": prev_msg["content"]}
                    )

            # Add current message
            formatted_messages.append({"role": "user", "content": message})

            # Call OpenAI API with updated format
            response = await self.client.chat.completions.create(
                model="gpt-4",  # or another appropriate model
                messages=formatted_messages,
                temperature=0.7,
                max_tokens=500,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "analyze_response",
                            "description": "Analyze the employee response and determine if escalation is needed",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "response_text": {
                                        "type": "string",
                                        "description": "The AI response to the employee",
                                    },
                                    "escalation_recommended": {
                                        "type": "boolean",
                                        "description": "Whether the employee's message indicates a situation that should be escalated to HR",
                                    },
                                    "escalation_reason": {
                                        "type": "string",
                                        "description": "The reason for escalation, if recommended",
                                    },
                                    "suggested_replies": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Suggested quick replies for the employee to choose from",
                                    },
                                    "sentiment_analysis": {
                                        "type": "object",
                                        "properties": {
                                            "primary_emotion": {
                                                "type": "string",
                                                "description": "Primary emotion detected in employee's message",
                                            },
                                            "urgency_level": {
                                                "type": "integer",
                                                "description": "Urgency level (1-5) of addressing the employee's concern",
                                            },
                                        },
                                    },
                                },
                                "required": [
                                    "response_text",
                                    "escalation_recommended",
                                    "suggested_replies",
                                ],
                            },
                        },
                    }
                ],
                tool_choice={
                    "type": "function",
                    "function": {"name": "analyze_response"},
                },
            )

            if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                function_args = json.loads(tool_call.function.arguments)

                return {
                    "content": function_args["response_text"],
                    "escalation_recommended": function_args["escalation_recommended"],
                    "escalation_reason": function_args.get("escalation_reason", ""),
                    "suggested_replies": function_args["suggested_replies"],
                    "sentiment_analysis": function_args.get("sentiment_analysis", {}),
                }
            else:
                raise ValueError("No tool call found in the response")

        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            # Fallback response
            return {
                "content": "I'm sorry, I'm having trouble processing that right now. Could you please try again or contact HR directly if you need immediate assistance?",
                "escalation_recommended": False,
                "escalation_reason": "",
                "suggested_replies": [
                    "Yes, I'll try again",
                    "I'll contact HR directly",
                    "Can you help me with something else?",
                ],
                "sentiment_analysis": {},
            }

    def _create_system_prompt(self, employee_data: Dict[str, Any]) -> str:
        """
        Create a system prompt with employee context
        """
        # Extract data safely
        vibe_data = employee_data.get("vibe_data", {})
        leave_data = employee_data.get("leave_data", {})
        performance_data = employee_data.get("performance_data", {})
        activity_data = employee_data.get("activity_data", {})
        rewards_data = employee_data.get("rewards_data", {})
        onboarding_data = employee_data.get("onboarding_data", {})

        system_prompt = f"""
        You are an empathetic AI assistant named "TIA" working in Deloitte's People Experience team. Your role is to analyze employee data, identify potential concerns, and have meaningful conversations with employees to understand their well-being and provide appropriate suggestions.

        CONTEXT:
        You have access to the following data for employee {employee_data.get("id", "Unknown")}:

        1. VIBEMETER DATA:
        - Response Date: {vibe_data.get("date", "Unknown")}
        - Vibe Score: {vibe_data.get("score", "Unknown")}/5
        - Emotion Zone: {vibe_data.get("zone", "Unknown")}

        2. LEAVE DATA:
        - Leave Type: {leave_data.get("type", "Unknown")}
        - Leave Days Taken (Year to Date): {leave_data.get("days_taken", "Unknown")}
        - Last Leave Start Date: {leave_data.get("start_date", "Unknown")}
        - Last Leave End Date: {leave_data.get("end_date", "Unknown")}

        3. ACTIVITY TRACKER:
        - Average Teams Messages Sent (Last 30 Days): {activity_data.get("avg_teams_messages", "Unknown")}
        - Average Emails Sent (Last 30 Days): {activity_data.get("avg_emails", "Unknown")}
        - Average Meetings Attended (Last 30 Days): {activity_data.get("avg_meetings", "Unknown")}
        - Average Work Hours (Last 30 Days): {activity_data.get("avg_work_hours", "Unknown")}

        4. PERFORMANCE DATA:
        - Review Period: {performance_data.get("review_period", "Unknown")}
        - Performance Rating: {performance_data.get("rating", "Unknown")}/5
        - Manager Feedback Summary: {performance_data.get("feedback", "Not available")}
        - Promotion Consideration: {performance_data.get("promotion_flag", "Unknown")}

        5. REWARDS & RECOGNITION:
        - Latest Award Type: {rewards_data.get("latest_award_type", "None")}
        - Latest Award Date: {rewards_data.get("latest_award_date", "Unknown")}
        - Reward Points (Year to Date): {rewards_data.get("points", "0")}

        6. ONBOARDING EXPERIENCE:
        - Joining Date: {onboarding_data.get("joining_date", "Unknown")}
        - Onboarding Feedback: {onboarding_data.get("feedback", "Not given")}
        - Mentor Assigned: {onboarding_data.get("mentor_assigned", "Unknown")}
        - Initial Training Completed: {onboarding_data.get("training_completed", "Unknown")}

        REFERENCE THRESHOLDS:
        {{
            "thresholds": {{
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
            }}
        }}

        YOUR TASK:
        1. Based on the data above, identify potential areas of concern for this employee
        2. Have a conversation with the employee to understand their well-being
        3. Ask relevant questions based on the data patterns
        4. Provide personalized suggestions
        5. Calculate a risk score based on their vibe, responses, and overall data
        6. Return a structured response

        CONVERSATION FLOW:
        1. Introduce yourself briefly
        2. Express interest in the employee's well-being
        3. Ask specific questions based on their data patterns (choose 3-5 most relevant questions)
        4. Listen to their feedback
        5. Provide supportive suggestions
        6. Thank them for their time

        [Question bank, risk score calc, and response format remain same...]
    """
        return system_prompt



openai_client = OpenAIClient()
