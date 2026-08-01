from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WordCreate(BaseModel):
    word: str
    translation: str
    example_sentence: Optional[str] = None


class WordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    word: str
    translation: str
    example_sentence: Optional[str] = None
    easiness_factor: float
    interval_days: int
    repetitions: int
    next_review_at: datetime
    last_reviewed_at: Optional[datetime] = None
    created_at: datetime


class ReviewSubmit(BaseModel):
    word_id: int
    quality: int = Field(ge=0, le=5, description="SM-2 recall quality, 0 (blackout) to 5 (perfect)")


class ReviewAccepted(BaseModel):
    task_id: str
    word_id: int
    status: str = "accepted"
