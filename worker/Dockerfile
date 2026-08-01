# Build context: repo root (english-mastery-app/), so this can COPY ../common
FROM python:3.11-slim

WORKDIR /app

COPY worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY common ./common
COPY worker ./worker

# --concurrency=2: without this, Celery's default prefork pool spawns one
# child process per detected CPU core immediately at startup - on a node
# with several cores, that can mean 4-8+ full Python processes before a
# single task runs, easily exceeding a modest memory limit right at boot.
# This workload is lightweight (simple SM-2 math, one DB write per task) and
# doesn't need process-per-core parallelism.
CMD ["celery", "-A", "worker.tasks", "worker", "--loglevel=info", "--concurrency=2"]
