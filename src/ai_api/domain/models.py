from pydantic import BaseModel, Field


class PredictIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)


class PredictOut(BaseModel):
    label: str
    score: float
    provider: str
    request_id: str
