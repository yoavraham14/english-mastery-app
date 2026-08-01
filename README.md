# English Mastery App

Spaced-repetition vocabulary study app. Built as the running project for the DevOps
Mastery Roadmap - the same app evolves across milestones to give each infrastructure
topic (containers, orchestration, CI/CD, cloud) a real workload to operate.

## Architecture

- **api** - FastAPI + SQLAlchemy + Pydantic. Add words, list words, fetch the next word
  due for review, submit a review result.
- **postgres** - stores words and SM-2 scheduling state (easiness factor, interval,
  repetitions, next/last review timestamps).
- **redis** - Celery message broker.
- **worker** - Celery worker. Recalculates SM-2 scheduling state asynchronously after a
  review is submitted, instead of doing it inline in the API request.
- **web** - static frontend served by nginx, which also reverse-proxies `/api/*` to the
  API service. The upstream address comes from the `API_HOST` environment variable, so
  the same image runs unchanged under Compose (`api:8000`) and Kubernetes
  (`api.<namespace>.svc.cluster.local:8000`) - build once, promote the artifact.

The API dispatches review-processing work by task name
(`worker.tasks.process_review`) via `celery_app.send_task(...)`, without importing the
worker's code directly, so the two services stay decoupled at the image level.

## Running locally

```bash
docker compose up --build
```

- UI: `http://localhost:8080`
- API: `http://localhost:8000` (interactive docs at `/docs`)

### Seeding the database

```bash
docker compose run --rm api python -m scripts.seed
```

Loads ~70 English words with Hebrew translations and example sentences. The script is
idempotent - existing words are skipped, so it is safe to run repeatedly. In Kubernetes
this becomes a Job rather than a Deployment.

## Endpoints

- `POST /words` - add a word (`word`, `translation`, optional `example_sentence`)
- `GET /words` - list all words
- `GET /words/next` - get the next word due for review
- `POST /reviews` - submit a review result (`word_id`, `quality` 0-5); processed
  asynchronously by the Celery worker
