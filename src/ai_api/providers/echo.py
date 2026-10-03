from ai_api.domain.models import PredictOut


class EchoProvider:
    """Deterministic provider so the template runs without a model file or API key."""

    name = "echo"

    def predict(self, text: str, request_id: str) -> PredictOut:
        stripped = text.strip()
        label = "empty" if not stripped else ("long" if len(stripped) > 80 else "ok")
        score = min(1.0, len(stripped) / 80)
        return PredictOut(label=label, score=round(score, 4), provider=self.name, request_id=request_id)
