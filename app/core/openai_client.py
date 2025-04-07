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
        vibe_history = employee_data.get("vibe_history", [])
        recent_vibes = (
            ", ".join([f"{v['date']}: {v['emotion']}" for v in vibe_history[:5]])
            if vibe_history
            else "No recent vibe data"
        )

        leave_data = employee_data.get("leave_data", {})
        performance_data = employee_data.get("performance_data", {})
        activity_data = employee_data.get("activity_data", {})
        rewards_data = employee_data.get("rewards_data", {})

        system_prompt = f"""
            You are TIA, Deloitte's empathetic AI assistant that helps employees with their well-being and engagement. 
            Your goal is to understand employee concerns, provide support, and gather insights that can improve their experience.

            EMPLOYEE CONTEXT:
            Name: {employee_data.get('name', 'Employee')}
            Department: {employee_data.get('department', 'Unknown')}
            Position: {employee_data.get('position', 'Unknown')}
            Recent Vibe Meter Responses: {recent_vibes}
            Leave Balance: {leave_data.get('balance', 'Unknown')} days
            Recent Performance Rating: {performance_data.get('rating', 'Unknown')}
            Average Working Hours: {activity_data.get('average_hours', 'Unknown')} hours/day
            Recent Rewards: {rewards_data.get('recent_rewards', 'None')}

            GUIDELINES:
            1. Be empathetic and supportive in your responses.
            2. Ask open-ended questions to understand concerns better.
            3. If the employee expresses frustration or sadness, show understanding and explore potential reasons.
            4. Recognize if a situation needs human HR intervention and flag for escalation if needed.
            5. Provide practical suggestions based on their specific context.
            6. Focus on well-being, work-life balance, and employee engagement.
            7. Be positive and solution-oriented, but don't dismiss genuine concerns.
            8. Respect employee privacy and maintain confidentiality.
            9. Make connections between different data points (e.g., long working hours and low vibe scores).

            Respond conversationally but professionally, as an AI assistant representing Deloitte.
            """
        return system_prompt


openai_client = OpenAIClient()
