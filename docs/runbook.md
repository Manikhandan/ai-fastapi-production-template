# On-call runbook for the serving API

The FastAPI starter treats `/ready` as "configured and provider constructed".
A 401 from a missing API key is expected when `AI_API_KEY` is set.
Rate-limit 429s are per-client within a sliding window; they are not a capacity claim.
