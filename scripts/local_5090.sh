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

check_ollama() {
  curl -fsS http://127.0.0.1:11434/api/version >/dev/null
  for model in qwen3.8:27b qwen3-embedding:8b dengcao/Qwen3-Reranker-4B:Q8_0; do
    ollama show "${model}" >/dev/null
  done
}

case "${1:-up}" in
  up)
    check_ollama
    compose up -d --build
    ;;
  dev)
    check_ollama
    compose up -d searxng searxng-mcp
    exec "${ROOT_DIR}/scripts/start_e2e.sh" \
      --config_file configs/config_web_local_5090.yml \
      --port 8000
    ;;
  pull)
    compose pull searxng postgres
    ;;
  configure-ollama)
    sudo install -D -m 0644 \
      "${ROOT_DIR}/deploy/ollama/aiq.conf" \
      /etc/systemd/system/ollama.service.d/aiq.conf
    sudo systemctl daemon-reload
    sudo systemctl restart ollama
    check_ollama
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
    echo "Usage: $0 {up|dev|pull|configure-ollama|down|logs [service]|status|validate}" >&2
    exit 2
    ;;
esac
