from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.data.vibemeter_analytics import get_employees_for_chat

class ChatService:
    """
    Service for handling chat-related functionality, particularly for sending
    messages to employees who need attention based on vibemeter data.
    """
    
    @staticmethod
    def get_employees_to_contact() -> List[Dict[str, str]]:
        """
        Fetches the list of employees who should be contacted via chat
        based on vibemeter analysis.
        
        Returns:
            List of dictionaries containing employee IDs.
        """
        return get_employees_for_chat()
    
    @staticmethod
    def prepare_chat_template(employee_id: str, 
                              concern_type: str = "general") -> Dict[str, str]:
        """
        Prepares a chat template for a specific employee based on the type of concern.
        
        Args:
            employee_id: The ID of the employee to contact
            concern_type: The type of concern (e.g., "low_vibe", "high_variability", "general")
            
        Returns:
            A dictionary containing chat template information
        """
        templates = {
            "low_vibe": {
                "subject": "Checking in - How are you doing?",
                "message": f"Hi {employee_id}, we noticed you might be going through a challenging time. "
                          "The HR team is here to support you. Would you like to schedule a quick chat?"
            },
            "high_variability": {
                "subject": "Touching base - Your wellbeing matters",
                "message": f"Hello {employee_id}, we've noticed some changes in your wellbeing metrics. "
                          "We'd love to check in and see how we can support you during this time."
            },
            "general": {
                "subject": "Checking in - Your wellbeing matters to us",
                "message": f"Hello {employee_id}, this is a quick check-in from the HR team. "
                          "How are you feeling today? Is there anything we can help with?"
            }
        }
        
        return templates.get(concern_type, templates["general"])
    
    @staticmethod
    def send_chat_message(employee_id: str, 
                          message: str, 
                          subject: Optional[str] = None) -> Dict[str, str]:
        """
        Sends a chat message to an employee.
        This is a placeholder implementation that would be replaced with actual
        chat service integration.
        
        Args:
            employee_id: The ID of the employee to send the message to
            message: The message content
            subject: The message subject (optional)
            
        Returns:
            Response indicating success or failure
        """
        # Placeholder for actual chat service implementation
        # In a real application, this would connect to a chat service API
        
        # Simulating successful message sending
        return {
            "status": "success",
            "message": f"Chat message sent to {employee_id}",
            "details": {
                "employee_id": employee_id,
                "subject": subject,
                "message_length": len(message)
            }
        }

def get_employees_for_chat_service() -> List[Dict[str, str]]:
    """
    Convenience function to get employees who need attention via chat.
    This can be imported and used directly by API routes.
    
    Returns:
        List of employee IDs who should be contacted
    """
    return ChatService.get_employees_to_contact()
