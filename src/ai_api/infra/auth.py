from fastapi import Header, HTTPException

from ai_api.config import Settings


def require_api_key(settings: Settings, x_api_key: str | None = Header(default=None)) -> None:
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="invalid api key")
