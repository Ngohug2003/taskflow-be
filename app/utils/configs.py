import sqlalchemy
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union, Any, Optional


load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore" # Bỏ qua các biến thừa để tránh lỗi
    )

    APP_NAME: str = "Task Flow API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DB_DRIVER: str = "postgresql+asyncpg"
    DATABASE_ECHO: bool = False
    
    # Auth
    SECRET_KEY: str = "changeme-super-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    GOOGLE_CLIENT_ID: Optional[str] = None
    
    # API
    API_PREFIX: str = "/v1"
    CORS_ORIGINS: Any = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            import json
            return json.loads(v)
        return v

    def get_db_url(self, to_string=False):
        if self.DATABASE_URL:
            return self.DATABASE_URL
        url = sqlalchemy.engine.url.URL.create(
            drivername=self.DB_DRIVER, 
            username=self.DB_USER,
            password=self.DB_PASSWORD, 
            host=self.DB_HOST, 
            port=self.DB_PORT,
            database=self.DB_NAME
        )
        if to_string:
            return url.render_as_string(hide_password=False)
        return url

project_settings = Settings()
