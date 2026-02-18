from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Domain Expansion API"
    app_version: str = "0.2.0"
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")


settings = Settings()
