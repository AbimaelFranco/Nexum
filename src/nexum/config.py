"""Configuración centralizada de Nexum, cargada desde variables de entorno.

Todos los servicios (bot, core, scheduler) importan `settings` desde aquí en
vez de leer `os.environ` directamente, para tener una única fuente de verdad
tipada y validada.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    telegram_bot_token: str = ""

    # Claude API (Anthropic)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-5"

    # PostgreSQL
    postgres_user: str = "nexum"
    postgres_password: str = "changeme"
    postgres_db: str = "nexum"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
