from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_ENV: str = "dev"
    APP_NAME: str = "ai-automation-control-center"
    DATABASE_URL: str = "postgresql+psycopg://aacc_user:CAMBIAR_VALOR@127.0.0.1:5432/aacc_db"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL debe estar configurada")
        return v


settings = Settings()
