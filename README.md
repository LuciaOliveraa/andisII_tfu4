# Flask Recipes API — TFU 4

This repository implements a REST API for managing recipes and products using Flask + PostgreSQL, with Docker Compose for easy deployment. Code is written in **English**, follows good practices, uses transactions (ACID via SQLAlchemy), and implements the requested architecture patterns:

- **Rate limiting** (Flask-Limiter)
- **Retry** strategy (tenacity on DB/IO operations)
- **Publisher-Subscriber** (Redis pub/sub for events)
- **Cache-aside** (Redis caching for read-heavy endpoints)
- **Valet key** (short-lived JWT tokens for delegated limited access)
- **Gatekeeper** (authorization middleware enforcing permissions)
- **(Additional)**: Logging, structured project layout, Docker + docker-compose
- **External Configuration Store**

## Project tree
```
flask_recipes_api/
├─ app/
│  ├─ __init__.py
│  ├─ app.py
│  ├─ auth.py
│  ├─ cache.py
│  ├─ config.py
│  ├─ db.py
│  ├─ events.py
│  ├─ models.py
│  ├─ schemas.py
│  ├─ routes/
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  ├─ products.py
│  │  ├─ recipes.py
│  │  └─ valet.py
│  ├─ worker.py
│  ├─ utils.py
│  ├─ scripts/
│  │  ├─ demo_cache.py
│  │  ├─ demo_pub_sub.py
│  │  ├─ demo_rate_limiting.py
│  │  ├─ demo_retry.py
│  │  ├─ demo_valet_gatekeeper.py
│  │  └─ run_all_demos.sh
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ README.md
```

## Prerequisites

- Docker & Docker Compose installed and available on your PATH
- (Optional) local Python 3.11+ virtualenv if you prefer running scripts on the host

## Quickstart — run everything (recommended)

1. Build and start services (web, db, redis, worker):

```bash
docker-compose up -d --build
```

2. Run all demo scripts in sequence using the included runner. From the repo root run:

```bash
bash scripts/run_all_demos.sh
```

The runner will:

- wait for the web service to respond on http://localhost:8000
- run the demos in this order: cache, pub/sub, retry, rate-limiting, valet+gatekeeper
- by default, tear down the stack after running demos (use --no-teardown to keep services running)

3. (Optional) Tear down services manually:

```bash
docker-compose down
```

## Runner script

The script `scripts/run_all_demos.sh` executes the full demo flow by invoking the demo scripts inside the running `web` container (so they can access Redis and the database). It sets `PYTHONPATH=/app` when running the scripts so the package `app` can be imported from `scripts/`.

Usage examples:

```bash
# run demos and tear down when finished
bash scripts/run_all_demos.sh

# run demos but keep services running afterwards
bash scripts/run_all_demos.sh --no-teardown
```

curl -sS -L -X GET "http://localhost:8000/config" -H "Accept: application/json"

## Notes and troubleshooting

- If you run demos on the host (outside the container), activate your virtualenv and run the demo scripts directly:

```bash
source .venv/bin/activate
python scripts/demo_cache.py
python scripts/demo_pub_sub.py
...etc...
```

- If a script fails to import `app`, make sure you run it from the repo root and that `PYTHONPATH` includes the repo root (the runner does this automatically when invoking via the container).
---