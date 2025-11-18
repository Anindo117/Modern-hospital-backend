"""Application Configuration"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import json
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Configuration
    APP_NAME: str = "Modern Hospital API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://hospital_user:secure_password@localhost:5432/hospital_db"
    DATABASE_ECHO: bool = False
    
    # JWT Configuration
    SECRET_KEY: str = "your-super-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000"]
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@hospital.com"
    FROM_NAME: str = "Modern Hospital"
    
    # Redis Configuration
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Phone Number Configuration
    PHONE_COUNTRY_CODE: str = "+1"
    PHONE_MIN_LENGTH: int = 10
    PHONE_MAX_LENGTH: int = 15
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()

# Post-initialization: Ensure CORS_ORIGINS is properly parsed
if isinstance(settings.CORS_ORIGINS, str):
    try:
        settings.CORS_ORIGINS = json.loads(settings.CORS_ORIGINS)
    except (json.JSONDecodeError, ValueError):
        settings.CORS_ORIGINS = [origin.strip() for origin in settings.CORS_ORIGINS.split(',')]

# Ensure it's a list
if not isinstance(settings.CORS_ORIGINS, list):
    settings.CORS_ORIGINS = list(settings.CORS_ORIGINS)
