from __future__ import annotations

import uuid

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse

from ai_api.config import Settings, get_settings
from ai_api.domain.models import PredictIn, PredictOut
from ai_api.infra.auth import require_api_key
from ai_api.infra.logging import configure_logging
from ai_api.infra.ratelimit import SlidingWindowLimiter
from ai_api.services.inference import InferenceService, provider_factory


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    service = InferenceService(
        provider_factory(settings.provider),
        timeout_s=settings.request_timeout_s,
        retries=settings.max_retries,
    )
    limiter = SlidingWindowLimiter(settings.rate_limit, settings.rate_window_s)
    app = FastAPI(title=settings.app_name, version="1.0.0")
    app.state.settings = settings
    app.state.service = service

    @app.middleware("http")
    async def context(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        client = request.client.host if request.client else "local"
        if not limiter.allow(client) and request.url.path == "/v1/predict":
            return JSONResponse({"error": "rate_limited"}, status_code=429)
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        rid = getattr(request.state, "request_id", "")
        headers = {"x-request-id": rid} if rid else {}
        return JSONResponse(
            {"error": "internal", "type": type(exc).__name__},
            status_code=500,
            headers=headers,
        )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready")
    def ready():
        svc = app.state.service
        name = getattr(svc.provider, "name", "")
        return {"ready": bool(name), "provider": name or None}

    @app.post("/v1/predict", response_model=PredictOut)
    def predict(body: PredictIn, request: Request, x_api_key: str | None = Header(default=None)):
        require_api_key(settings, x_api_key)
        return request.app.state.service.predict(body, request.state.request_id)

    @app.get("/")
    def root():
        return {"service": settings.app_name, "docs": "/docs"}

    return app


app = create_app()
