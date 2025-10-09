# backend/app/core/config.py
from pydantic import BaseModel
from .constants import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    POSTGRES_SERVER,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
    POSTGRES_PORT,
    REDIS_HOST,
    REDIS_PORT,
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
)

class Settings(BaseModel):
    # App
    APP_NAME: str = "Makhzen API"
    VERSION: str = "0.1"
    
    # Security
    secret_key: str = SECRET_KEY
    algorithm: str = ALGORITHM
    access_token_expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES

    # Database
    postgres_server: str = POSTGRES_SERVER
    postgres_user: str = POSTGRES_USER
    postgres_password: str = POSTGRES_PASSWORD
    postgres_db: str = POSTGRES_DB
    postgres_port: int = POSTGRES_PORT

    # Redis
    redis_host: str = REDIS_HOST
    redis_port: int = REDIS_PORT

    # Celery
    celery_broker_url: str = CELERY_BROKER_URL
    celery_result_backend: str = CELERY_RESULT_BACKEND

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

settings = Settings()