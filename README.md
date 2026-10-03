# AI FastAPI Production Starter

A starter another engineer can clone for an inference API. The point is the layering, not a clever model.

```
api (FastAPI, request ids, /health, /ready)
  → service (retries around a provider)
    → provider (Protocol; EchoProvider is the default)
domain models are Pydantic.
config is pydantic-settings with an `AI_` prefix.
auth is an optional API key.
rate limiting is a sliding window on `/v1/predict`.
```

Replace `EchoProvider` with a model file or an HTTP client. Do not put that logic in the route.

## Local setup

```bash
pip install -e ".[dev]"
cp .env.example .env
uvicorn ai_api.main:app --port 8000
```

Set `AI_API_KEY` before exposing the port beyond localhost.

## Tests

```bash
ruff check src tests
pytest -q
```

## Security

- Empty `AI_API_KEY` disables auth so local tests stay simple. That is not a production default you should ship.
- Non-root container user 10001.
- Request bodies are schema-validated.

## Trade-offs

- Sync provider call. If the real model is remote and slow, make the provider async and add a timeout around the HTTP client, not around FastAPI itself.
- In-memory rate limiter is per replica.

## What I would improve next

- OpenTelemetry traces instead of request-id headers only.
- A second provider that calls HTTP with `httpx` timeouts.
