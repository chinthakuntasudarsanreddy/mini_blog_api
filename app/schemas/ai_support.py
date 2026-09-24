from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AISupportRequest(BaseModel):
    message: str


class AISupportResponse(BaseModel):
    id: int
    question: str
    ai_response: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)