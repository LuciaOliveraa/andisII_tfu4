#!/usr/bin/env bash
# Runs docker-compose, waits for services, runs all demo scripts inside the web container,
# and optionally tears down the stack.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_CMD="docker-compose"
WEB_SERVICE="web"
HOST_URL="http://localhost:8000"

TEARDOWN=true

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-teardown) TEARDOWN=false; shift ;;
        -h|--help)
        echo "Usage: $0 [--no-teardown]"
        exit 0
        ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "Starting services with docker-compose..."
${COMPOSE_CMD} up -d --build

echo "Waiting for ${HOST_URL} to become available (timeout 60s)..."
MAX_WAIT=60
WAITED=0
until [ "$WAITED" -ge "$MAX_WAIT" ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${HOST_URL} || true)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "Service is up"
        break
    fi
    sleep 1
    WAITED=$((WAITED+1))
done

if [ "$WAITED" -ge "$MAX_WAIT" ]; then
    echo "Warning: service did not become ready within ${MAX_WAIT}s, continuing anyway..."
fi

RUN_IN_CONTAINER() {
    local script_path="$1"
    echo "\n>>> Running ${script_path} inside ${WEB_SERVICE} container"
    # use -T to avoid TTY allocation issues in some CI
    ${COMPOSE_CMD} exec -T -w /app ${WEB_SERVICE} env PYTHONPATH=/app python "${script_path}"
}

pushd "${ROOT_DIR}" > /dev/null

RUN_IN_CONTAINER scripts/demo_cache.py
RUN_IN_CONTAINER scripts/demo_pub_sub.py
RUN_IN_CONTAINER scripts/demo_retry.py
RUN_IN_CONTAINER scripts/demo_rate_limiting.py
RUN_IN_CONTAINER scripts/demo_valet_gatekeeper.py

popd > /dev/null

if [ "$TEARDOWN" = true ]; then
    echo "Tearing down docker-compose stack..."
    ${COMPOSE_CMD} down
else
    echo "Leaving services running (use 'docker-compose down' to stop them)."
fi

echo "All demos finished."
