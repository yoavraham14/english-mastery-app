from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from common.celery_app import celery_app
from common.database import Base, engine, get_db
from common.models import Word
from common.schemas import ReviewAccepted, ReviewSubmit, WordCreate, WordOut

app = FastAPI(title="English Mastery API")

Base.metadata.create_all(bind=engine)


@app.post("/words", response_model=WordOut, status_code=201)
def add_word(payload: WordCreate, db: Session = Depends(get_db)):
    word = Word(
        word=payload.word,
        translation=payload.translation,
        example_sentence=payload.example_sentence,
    )
    db.add(word)
    db.commit()
    db.refresh(word)
    return word


@app.get("/words", response_model=list[WordOut])
def list_words(db: Session = Depends(get_db)):
    return db.execute(select(Word).order_by(Word.id)).scalars().all()


@app.get("/words/next", response_model=WordOut)
def get_next_word(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    word = (
        db.execute(
            select(Word)
            .where(Word.next_review_at <= now)
            .order_by(Word.next_review_at)
            .limit(1)
        )
        .scalars()
        .first()
    )
    if word is None:
        raise HTTPException(status_code=404, detail="No word due for review")
    return word


@app.post("/reviews", response_model=ReviewAccepted, status_code=202)
def submit_review(payload: ReviewSubmit, db: Session = Depends(get_db)):
    word = db.get(Word, payload.word_id)
    if word is None:
        raise HTTPException(status_code=404, detail="Word not found")

    task = celery_app.send_task(
        "worker.tasks.process_review",
        args=[payload.word_id, payload.quality],
    )
    return ReviewAccepted(task_id=task.id, word_id=payload.word_id)
