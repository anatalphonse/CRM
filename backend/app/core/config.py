from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CRM"
    DATABASE_URL: str = "postgresql://postgres:1236@localhost:5432/crm_db"

    class config:
        env_file = ".env"

settings = Settings()