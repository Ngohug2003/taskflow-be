from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union, Any
import json


class Settings(BaseSettings):
    APP_NAME: str = "Task Flow API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/taskflow"
    DATABASE_ECHO: bool = False

    # Auth
    SECRET_KEY: str = "changeme-super-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: Any = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
