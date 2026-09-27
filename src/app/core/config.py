# settings from .env
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    secret_key: str = "change-me"
    access_token_minutes: int = 15
    refresh_token_days: int = 7


settings = Settings()