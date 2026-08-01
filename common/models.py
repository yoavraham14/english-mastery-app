from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from common.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False, index=True)
    translation = Column(String, nullable=False)
    example_sentence = Column(String, nullable=True)

    # SM-2 scheduling state
    easiness_factor = Column(Float, nullable=False, default=2.5)
    interval_days = Column(Integer, nullable=False, default=0)
    repetitions = Column(Integer, nullable=False, default=0)
    next_review_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
