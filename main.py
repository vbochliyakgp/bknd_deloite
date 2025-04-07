# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

from app.api import auth, chatbot, hr, admin
from app.database import Base, engine
from app.config import settings
import logging

from dotenv import load_dotenv, dotenv_values

# loading variables from .env file
load_dotenv()


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Create database tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"[{datetime.now().isoformat()}] {request.method} {request.url.path}")
    response = await call_next(request)
    return response

# Include routers
app.include_router(
    auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"]
)
app.include_router(
    chatbot.router, prefix=f"{settings.API_V1_STR}/chatbot", tags=["Chatbot"]
)
app.include_router(hr.router, prefix=f"{settings.API_V1_STR}/hr", tags=["HR Dashboard"])
app.include_router(
    admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin Dashboard"]
)


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "description": "API for the Vibemeter employee well-being system",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
