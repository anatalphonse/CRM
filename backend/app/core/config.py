from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
from pydantic import ConfigDict
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

class Settings(BaseSettings):

    model_config = ConfigDict(extra="ignore")

    PROJECT_NAME: str = "CRM"
    DATABASE_URL: str = DATABASE_URL

    ENVIRONMENT: str = ENVIRONMENT

    # Security settings
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1","*"]
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",    # React dev server
        "http://localhost:3001",    # Alternative React port
        "http://localhost:8000",    # FastAPI
        "http://localhost:8080",    # Alternative backend
        "http://localhost:5173",    # Vite dev server
        "http://localhost:4200",    # Angular dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080"
    ]
    # API Configuration
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "CRM Backend API"
    API_DESCRIPTION: str  = "A comprehensive CRM system backend"

    # Security
    SECRET_KEY: str =  SECRET_KEY
    ALGORITHM: str = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES: int = ACCESS_TOKEN_EXPIRE_MINUTES

    # Use model_config instead of class Config
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # This allows extra fields from .env without error
    )

settings = Settings()