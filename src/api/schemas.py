from pydantic import BaseModel
from typing import Any

class InferenceRequest(BaseModel):
    """Schema for inference request."""
    data: Any


class InferenceResponse(BaseModel):
    """Schema for inference response."""
    results: Any