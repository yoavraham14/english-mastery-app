from datetime import datetime, timedelta, timezone

from common.celery_app import celery_app
from common.database import SessionLocal
from common.models import Word
from common.sm2 import calculate_sm2


@celery_app.task(name="worker.tasks.process_review")
def process_review(word_id: int, quality: int) -> None:
    db = SessionLocal()
    try:
        word = db.get(Word, word_id)
        if word is None:
            return

        result = calculate_sm2(
            quality=quality,
            repetitions=word.repetitions,
            easiness_factor=word.easiness_factor,
            interval_days=word.interval_days,
        )

        now = datetime.now(timezone.utc)
        word.repetitions = result.repetitions
        word.easiness_factor = result.easiness_factor
        word.interval_days = result.interval_days
        word.last_reviewed_at = now
        word.next_review_at = now + timedelta(days=result.interval_days)

        db.commit()
    finally:
        db.close()
