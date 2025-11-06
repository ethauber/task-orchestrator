from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Task Orchestrator'
    ollama_base_url: Optional[str] = None
    model_name: Optional[str] = None
    temperature: float = 0.114942  # Kepler-Bouwkamp

    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
    ]

    debug: bool = False
    database_url: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file='backend/.env'
    )
