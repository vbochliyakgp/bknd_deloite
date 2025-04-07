# Vibemeter Analytics

This module provides functionality to analyze vibemeter data and identify employees who need attention or support based on their emotional state.

## Files

- `vibemeter_dataset.csv` - The dataset containing employee vibemeter responses
- `vibemeter_analytics.py` - Core analytics functions to process the vibemeter data
- `chat_employees_util.py` - Utility script to demonstrate the analysis and message preparation workflow

## Key Features

1. **Employee Analysis**
   - Identifies employees with consistently low vibe scores (bottom 40%)
   - Identifies employees with high emotional variability (top 15%)
   - Combines these insights to create a prioritized list of employees to contact

2. **Chat Service Integration**
   - Provides functions to retrieve employees needing attention
   - Generates appropriate message templates based on the type of concern
   - Simulates sending messages to employees (actual implementation would connect to a chat service)

## Usage

### Using the Analytics Module

```python
from app.data.vibemeter_analytics import analyze_vibemeter, get_employees_for_chat

# Get separate lists of employees with low vibes and high emotional variability
low_vibe_employees, high_variability_employees = analyze_vibemeter()

# Get a combined, deduplicated list of all employees to contact
employees_to_contact = get_employees_for_chat()
```

### Using the Chat Service

```python
from app.services.chat import ChatService

# Get employees needing attention
employees = ChatService.get_employees_to_contact()

# For each employee, prepare and send a message
for emp in employees:
    employee_id = emp['Employee_ID']
    
    # Get appropriate template
    template = ChatService.prepare_chat_template(
        employee_id, 
        concern_type="low_vibe"  # or "high_variability" or "general"
    )
    
    # Send the message
    result = ChatService.send_chat_message(
        employee_id=employee_id,
        message=template["message"],
        subject=template["subject"]
    )
```

### Running the Utility Script

```bash
# Run directly
python -m app.data.chat_employees_util

# Alternatively, make it executable (on Unix systems)
chmod +x app/data/chat_employees_util.py
./app/data/chat_employees_util.py
```

## Implementation Details

The vibemeter analysis is performed using the following algorithm:

1. Load the vibemeter dataset
2. Separate employees with single entries from those with multiple entries
3. For employees with single entries:
   - Identify those with vibe scores in the lowest 40% as needing attention
4. For employees with multiple entries:
   - Calculate emotional variability (mean difference from average score)
   - Identify those with variability in the top 15% as needing attention
5. Combine both lists, removing duplicates
6. Prepare appropriate message templates based on the type of concern

## Extending the Implementation

To extend this implementation:

1. **Custom Analytics**: Add new analytics functions in `vibemeter_analytics.py`
2. **Additional Templates**: Add more message templates in the `ChatService.prepare_chat_template` method
3. **Real Chat Integration**: Replace the placeholder `send_chat_message` implementation with a real chat service integration 