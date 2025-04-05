#!/bin/bash

# Create the root directory
mkdir -p 
# Create root-level files
touch main.py
touch config.py
touch requirements.txt
touch Dockerfile
touch docker-compose.yml

# Create app directory and its __init__.py
mkdir -p app
touch app/__init__.py
touch app/database.py
touch app/dependencies.py

# Create API directory and files
mkdir -p app/api
touch app/api/__init__.py
touch app/api/auth.py
touch app/api/chatbot.py
touch app/api/hr.py
touch app/api/admin.py

# Create core directory and files
mkdir -p app/core
touch app/core/__init__.py
touch app/core/auth.py
touch app/core/security.py
touch app/core/openai_client.py

# Create models directory and files
mkdir -p app/models
touch app/models/__init__.py
touch app/models/user.py
touch app/models/employee.py
touch app/models/vibemeter.py
touch app/models/chat_session.py
touch app/models/message.py
touch app/models/leave.py
touch app/models/activity.py
touch app/models/performance.py
touch app/models/rewards.py

# Create schemas directory and files
mkdir -p app/schemas
touch app/schemas/__init__.py
touch app/schemas/user.py
touch app/schemas/employee.py
touch app/schemas/auth.py
touch app/schemas/chat.py
touch app/schemas/vibemeter.py
touch app/schemas/analytics.py

# Create services directory and files
mkdir -p app/services
touch app/services/__init__.py
touch app/services/employee.py
touch app/services/chat.py
touch app/services/analytics.py
touch app/services/email.py
touch app/services/report.py

# Create utils directory and files
mkdir -p app/utils
touch app/utils/__init__.py
touch app/utils/helper.py

echo "Directory structure for created successfully!"