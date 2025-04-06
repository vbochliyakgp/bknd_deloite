# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Vibemeter API"

    # JWT Settings
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "your-secret-key-here-change-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # In your config.py file
    SUPABASE_USER: str = "postgres"  # Usually "postgres"
    SUPABASE_PASSWORD: str = os.getenv("SUPABASE_PASSWORD", "")
    SUPABASE_HOST: str = "db.nbvwwbvarqitzeimgwfy.supabase.co"
    SUPABASE_PORT: str = "5432"  # Default PostgreSQL port
    SUPABASE_DB: str = "postgres"  # Usually "postgres" in Supabase

    # PostgreSQL Settings
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "vibemeter_db")

    # Email Settings
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "noreply@example.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "Vibemeter Bot")

    # API keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ELEVEN_LABS_API_KEY: str = os.getenv("ELEVEN_LABS_API_KEY", "")

    # Voice ID for ElevenLabs
    VOICE_ID: str = os.getenv("VOICE_ID", "cgSgspJ2msm6clMCkdW9")

    SELF_HOSTED_WHISPER_URL: str = os.getenv("SELF_HOSTED_WHISPER_URL", "")
    # CORS settings
    CORS_ORIGIN: str = os.getenv("CORS_ORIGIN", "http://localhost:5173")

    # Audio settings
    AUDIO_DIR: str = "audios"
    INCOMING_AUDIO_DIR: str = "incoming_audios"

    # OpenAI settings
    OPENAI_MODEL: str = "gpt-3.5-turbo-0125"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.6

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
