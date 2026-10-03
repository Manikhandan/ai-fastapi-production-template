from __future__ import annotations

from ai_api.domain.models import PredictIn, PredictOut
from ai_api.providers.base import InferenceProvider


class InferenceService:
    def __init__(self, provider: InferenceProvider, timeout_s: float, retries: int) -> None:
        self.provider = provider
        self.timeout_s = timeout_s
        self.retries = retries

    def predict(self, payload: PredictIn, request_id: str) -> PredictOut:
        last_error: Exception | None = None
        attempts = self.retries + 1
        for _ in range(attempts):
            try:
                return self.provider.predict(payload.text, request_id)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        assert last_error is not None
        raise last_error


def provider_factory(name: str) -> InferenceProvider:
    if name == "echo":
        from ai_api.providers.echo import EchoProvider

        return EchoProvider()
    raise ValueError(f"unknown provider {name}")
