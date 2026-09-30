# Local RTX 5090 deployment

This profile runs every AI-Q language-model role and document embedding locally.
Tavily is optional; SearXNG is the default web-search source.

## Services

| Service | Local URL | Purpose |
| --- | --- | --- |
| AI-Q UI | http://localhost:3000 | Research interface |
| AI-Q API | http://localhost:8000 | Jobs, chat, and knowledge APIs |
| vLLM | http://localhost:8001/v1 | `openai/gpt-oss-20b` on the RTX 5090 |
| Embeddings | http://localhost:8081/v1 | CPU `BAAI/bge-small-en-v1.5` |
| SearXNG | http://localhost:8888 | Local metasearch |
| SearXNG MCP | http://localhost:9901/mcp | AI-Q search-tool adapter |

## Start

```bash
cd /home/k8s/aiq
./scripts/local_5090.sh validate
./scripts/local_5090.sh pull
./scripts/local_5090.sh up
./scripts/local_5090.sh status
```

The first start downloads the vLLM image and roughly 14 GB of GPT-OSS weights.
Follow model startup with:

```bash
./scripts/local_5090.sh logs local-llm
```

Add `TAVILY_API_KEY` to `deploy/.env` only if the hosted fallback is wanted.
No hosted LLM API key is needed. `NVIDIA_API_KEY=local` is a compatibility
placeholder used by the LlamaIndex NVIDIA embedding client against the local
OpenAI-compatible embedding endpoint.

## Health checks

```bash
curl -fsS http://localhost:8001/health
curl -fsS http://localhost:8001/v1/models
curl -fsS http://localhost:8081/health
curl -fsS 'http://localhost:8888/search?q=NVIDIA&format=json'
curl -fsS http://localhost:8000/health
```

Test local embeddings:

```bash
curl -fsS http://localhost:8081/v1/embeddings \
  -H 'Content-Type: application/json' \
  -d '{"model":"BAAI/bge-small-en-v1.5","input":["local research"]}'
```

## Operations

```bash
# Service logs
./scripts/local_5090.sh logs aiq-agent

# Stop containers while preserving models and data
./scripts/local_5090.sh down

# Remove all persisted data only when intentionally resetting the installation
docker compose \
  -f deploy/compose/docker-compose.yaml \
  -f deploy/compose/docker-compose.local.yml \
  down --volumes
```

Uploaded documents and reports persist in the `aiq-local-data` volume. Model
weights persist in `hf-models`; embedding weights persist in
`embedding-models`.

## Resource limits

The profile limits deep-research worker concurrency to two model requests and
admits one deep-research job at a time. If vLLM reports an out-of-memory error,
lower `--max-model-len` from `32768` to `24576` in
`deploy/compose/docker-compose.local.yml`.

## Privacy boundary

LLM inference, embeddings, uploaded documents, checkpoints, and reports stay
local. Web queries necessarily leave the machine:

- SearXNG sends them to its enabled public search engines.
- Tavily receives them only when the Tavily source is explicitly selected and
  `TAVILY_API_KEY` is configured.
