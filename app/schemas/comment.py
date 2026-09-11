from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000
    )


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True