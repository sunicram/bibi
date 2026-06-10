import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str = "bibi_admin"
    POSTGRES_PASSWORD: str = "secure_password_replace_me"
    POSTGRES_DB: str = "bibi_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    JWT_SECRET_KEY: str = "your_secret_key_needs_to_be_long_and_secure_replace_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    TELEGRAM_BOT_TOKEN: str = "dummy_token"
    TELEGRAM_WEBHOOK_SECRET: str = "dummy_secret"

    OPENAI_API_KEY: str = "dummy_openai_key"
    ANTHROPIC_API_KEY: str = "dummy_anthropic_key"

    COACH_MODEL: str = "gpt-4o-mini"
    REVIEWER_MODEL: str = "claude-3-5-sonnet-20241022"

    MAX_CTL_RAMP_RATE: float = 7.0
    TSS_GUARDRAIL_PERCENT: float = 0.20

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
