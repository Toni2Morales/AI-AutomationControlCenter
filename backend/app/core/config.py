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
    DATABASE_URL: str = "postgresql+psycopg://aacc_user:CAMBIAR_VALOR@postgres:5432/aacc_db"
    BACKEND_CORS_ORIGINS: str = "http://localhost:4200,http://127.0.0.1:4200"
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b-instruct"
    OLLAMA_TIMEOUT: int = 120
    N8N_BASE_URL: str = "http://n8n:5678"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL debe estar configurada")
        return v

    @property
    def cors_origins(self) -> list[str]:
        """Devuelve los orígenes CORS configurados, sin entradas vacías."""
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()
