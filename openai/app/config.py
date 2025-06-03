from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings that can be loaded from environment variables."""
    
    # OpenAI API settings
    openai_api_key: str
    
    # Optional application settings
    app_name: str = "Text to Image API"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings. Results are cached for performance.
    
    Returns:
        Settings: Application settings
    """
    return Settings()
