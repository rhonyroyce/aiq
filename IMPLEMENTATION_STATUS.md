# Implementation status

Paused on 2026-09-30 at the user's request.

## Completed

- Cloned and pinned NVIDIA AI-Q `v2.2.0`.
- Installed the Python 3.13 environment, AI-Q packages, MCP environment, UI
  dependencies, and pre-commit hooks.
- Added the local RTX 5090 AI-Q profile:
  `configs/config_web_local_5090.yml`.
- Added Docker Compose definitions for vLLM, local CPU embeddings, SearXNG,
  the SearXNG MCP adapter, AI-Q, PostgreSQL, and the frontend.
- Added local embedding and SearXNG MCP integration source.
- Added `scripts/local_5090.sh`, `deploy/.env`, and `LOCAL_DEPLOYMENT.md`.
- Validated the merged Compose configuration and Python syntax.

## Paused operation

The `vllm/vllm-openai:latest` image pull was stopped while still downloading.
Docker retains completed/partial layers, so the pull should resume rather than
restart from zero.

## Pending, in order

1. Resume the vLLM image pull and pin its validated digest.
2. Start vLLM, download `openai/gpt-oss-20b`, and validate GPU inference and
   structured tool calls.
3. Validate the AI-Q local model profile against the running endpoint.
4. Build/start the CPU embedding service and test document ingestion/retrieval.
5. Build/start SearXNG and its MCP adapter; test search and source registration.
6. Start the full stack and run shallow, deep, document-only, and mixed-source
   acceptance tests.

## Resume command

```bash
cd /home/k8s/aiq
docker compose \
  --env-file deploy/.env \
  -f deploy/compose/docker-compose.yaml \
  -f deploy/compose/docker-compose.local.yml \
  pull local-llm
```
