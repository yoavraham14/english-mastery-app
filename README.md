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

## Running locally (Docker Compose)

Simplest way to run the full stack for local development - no cluster required.

```bash
docker compose up --build
```

- UI: `http://localhost:8080`
- API: `http://localhost:8000` (interactive docs at `/docs`)

### Seeding the database

```bash
docker compose run --rm api python -m scripts.seed
```

Loads ~135 English words with Hebrew translations and example sentences, drawn from
real DevOps/production vocabulary. The script is idempotent - existing words are
skipped, so it is safe to run repeatedly.

## Running on Kubernetes (Helm)

The full stack (api, worker, postgres, redis, web, plus Ingress and an HPA for the
api) is packaged as a Helm chart at `charts/english-mastery/`. Requires a running
cluster (e.g. a local Kind cluster) and an Ingress controller (ingress-nginx)
installed separately.

### First-time setup

Copy the example secrets file and fill in real values - `values-secrets.yaml` is
gitignored and must never be committed:

```bash
cp charts/english-mastery/values-secrets.example.yaml charts/english-mastery/values-secrets.yaml
# edit values-secrets.yaml with real Postgres credentials
```

### Install

```bash
helm install english-mastery ./charts/english-mastery \
  -f charts/english-mastery/values-secrets.yaml \
  --rollback-on-failure
```

### Upgrade (after changing values.yaml, or to deploy a new image tag)

```bash
helm upgrade english-mastery ./charts/english-mastery \
  -f charts/english-mastery/values-secrets.yaml \
  --rollback-on-failure
```

To deploy a specific image built by CI (see below) without editing `values.yaml`:

```bash
helm upgrade english-mastery ./charts/english-mastery \
  -f charts/english-mastery/values-secrets.yaml \
  --set api.image=ghcr.io/<username>/english-mastery-app \
  --set api.imageTag=<sha-tag-from-ghcr> \
  --rollback-on-failure
```

**Note (local Kind clusters only):** GHCR images are not automatically reachable by
a local cluster's nodes. Pull and load the image manually before upgrading:

```bash
docker pull ghcr.io/<username>/english-mastery-app:<sha-tag>
kind load docker-image ghcr.io/<username>/english-mastery-app:<sha-tag> --name <cluster-name>
```

### Seeding the database (Kubernetes)

```bash
kubectl exec -it <api-pod-name> -- python -m scripts.seed
```

### Uninstall

```bash
helm uninstall english-mastery
```

## CI

`.github/workflows/build-api.yml` builds the `api` image and pushes it to GHCR
(tagged `latest` and `sha-<commit-sha>`) on every push to `main` that touches `api/**`
or `common/**`. This is CI only, not CD - deploying the new image to a cluster is a
manual step (see `helm upgrade` above), since GitHub-hosted runners have no network
path to a local Kind cluster.

## Endpoints

- `POST /words` - add a word (`word`, `translation`, optional `example_sentence`)
- `GET /words` - list all words
- `GET /words/next` - get the next word due for review
- `POST /reviews` - submit a review result (`word_id`, `quality` 0-5); processed
  asynchronously by the Celery worker
