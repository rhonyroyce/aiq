#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_DIR="${ROOT_DIR}/deploy/compose"
ENV_FILE="${ROOT_DIR}/deploy/.env"
BASE_COMPOSE="${COMPOSE_DIR}/docker-compose.yaml"
LOCAL_COMPOSE="${COMPOSE_DIR}/docker-compose.local.yml"

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${ROOT_DIR}/deploy/.env.example" "${ENV_FILE}"
fi

compose() {
  docker compose \
    --env-file "${ENV_FILE}" \
    -f "${BASE_COMPOSE}" \
    -f "${LOCAL_COMPOSE}" \
    "$@"
}

case "${1:-up}" in
  up)
    compose up -d --build
    ;;
  pull)
    compose pull local-llm searxng postgres
    ;;
  down)
    compose down
    ;;
  logs)
    compose logs -f "${2:-aiq-agent}"
    ;;
  status)
    compose ps
    ;;
  validate)
    compose config --quiet
    ;;
  *)
    echo "Usage: $0 {up|pull|down|logs [service]|status|validate}" >&2
    exit 2
    ;;
esac
