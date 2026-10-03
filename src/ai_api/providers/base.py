from __future__ import annotations

from typing import Protocol

from ai_api.domain.models import PredictOut


class InferenceProvider(Protocol):
    name: str

    def predict(self, text: str, request_id: str) -> PredictOut: ...
