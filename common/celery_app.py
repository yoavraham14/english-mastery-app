import os

from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "english_mastery",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Prefork worker processes don't return freed memory to the OS between
    # tasks (a well-known characteristic of Python + C extensions like
    # psycopg2, not a leak in this code). Recycling each child process after
    # a bounded number of tasks caps memory growth instead of letting it
    # climb indefinitely.
    worker_max_tasks_per_child=100,
)
