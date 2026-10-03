from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AI_", env_file=".env", extra="ignore")

    app_name: str = "ai-api"
    log_level: str = "INFO"
    api_key: str = ""
    provider: str = "echo"
    request_timeout_s: float = 5.0
    max_retries: int = 1
    rate_limit: int = 60
    rate_window_s: float = 60.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
