"""
Configuration settings loaded from environment variables
All services use FREE TIER
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment"""
    
    # Pinecone (Free: 1 index, 100K vectors)
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "customer-support"
    
    # Groq (Free: 30 RPM, 6000 TPM)
    GROQ_API_KEY: str = ""
    
    # HuggingFace (Optional)
    HF_TOKEN: str = ""
    
    # n8n Webhook
    N8N_WEBHOOK_URL: str = ""
    
    # App Settings
    APP_NAME: str = "AI Support Assistant"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()