from fastapi.testclient import TestClient

from ai_api.config import Settings
from ai_api.main import create_app
from ai_api.providers.echo import EchoProvider


def test_echo_provider():
    out = EchoProvider().predict("hello", "rid")
    assert out.label == "ok"
    assert out.provider == "echo"


def test_predict_and_auth():
    app = create_app(Settings(api_key="secret", provider="echo"))
    client = TestClient(app)
    denied = client.post("/v1/predict", json={"text": "hello"})
    assert denied.status_code == 401
    ok = client.post("/v1/predict", json={"text": "hello"}, headers={"x-api-key": "secret"})
    assert ok.status_code == 200
    assert ok.json()["label"] == "ok"
    assert ok.headers["x-request-id"]
    assert client.get("/ready").json()["ready"] is True
    bad = client.post("/v1/predict", json={"text": ""}, headers={"x-api-key": "secret"})
    assert bad.status_code == 422


def test_unknown_provider():
    try:
        create_app(Settings(provider="missing"))
        assert False
    except ValueError:
        pass


def test_rate_limit_and_request_id():
    app = create_app(Settings(api_key="", provider="echo", rate_limit=1, rate_window_s=60))
    client = TestClient(app)
    headers = {"x-request-id": "fixed-id"}
    first = client.post("/v1/predict", json={"text": "hello"}, headers=headers)
    assert first.status_code == 200
    assert first.headers["x-request-id"] == "fixed-id"
    second = client.post("/v1/predict", json={"text": "hello"})
    assert second.status_code == 429
    assert second.json()["error"] == "rate_limited"


def test_provider_failure_retries():
    from ai_api.domain.models import PredictIn
    from ai_api.services.inference import InferenceService

    class Boom:
        name = "boom"

        def predict(self, text: str, request_id: str):
            raise TimeoutError("provider timeout")

    service = InferenceService(Boom(), timeout_s=1.0, retries=1)
    try:
        service.predict(PredictIn(text="hello"), "rid")
        assert False
    except TimeoutError:
        pass


def test_structured_provider_error_and_readiness():
    from ai_api.services.inference import InferenceService

    class Dead:
        name = ""

        def predict(self, text: str, request_id: str):
            raise RuntimeError("provider down")

    app = create_app(Settings(api_key="secret", provider="echo"))
    app.state.service = InferenceService(Dead(), timeout_s=1.0, retries=0)
    client = TestClient(app, raise_server_exceptions=False)
    assert client.get("/ready").json()["ready"] is False
    blown = client.post(
        "/v1/predict",
        json={"text": "hello"},
        headers={"x-api-key": "secret"},
    )
    assert blown.status_code == 500
    assert blown.json()["error"] == "internal"
    assert blown.headers["x-request-id"]
