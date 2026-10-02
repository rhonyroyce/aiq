# Local RTX 5090 deployment

This profile runs every AI-Q language-model role, document embedding, and
reranking operation through the host Ollama service. Tavily is optional;
SearXNG is the default web-search source.

## Local model policy

- Research, planning, writing, and summaries: `qwen3.8:27b`
- Document embeddings: `qwen3-embedding:8b`
- Retrieval reranking: `dengcao/Qwen3-Reranker-4B:Q8_0`
- `OLLAMA_MAX_LOADED_MODELS=1` prevents simultaneous model residency.
- `OLLAMA_NUM_PARALLEL=1` prevents concurrent generations from multiplying KV
  cache usage.
- Ollama detects available VRAM and evicts the current model before loading the
  next one. The deployment limits context to 65,536 tokens and uses a Q8 KV
  cache to fit the RTX 5090 safely.

The reranker is used as a sequential relevance gate after vector retrieval.
Ollama 0.32 does not expose `/api/rerank`, so AI-Q sends the model's documented
yes/no prompt through `/api/generate`, then unloads it before research begins.

## Configure and start

```bash
cd /home/k8s/aiq

# Install the checked-in Ollama memory/concurrency policy and restart Ollama.
./scripts/local_5090.sh configure-ollama

./scripts/local_5090.sh validate
./scripts/local_5090.sh pull

# Recommended in WSL: search services in Docker, AI-Q and its UI on the host.
./scripts/local_5090.sh dev
```

Keep that terminal open, then browse to http://localhost:3000. The API is at
http://localhost:8000, SearXNG at http://localhost:8888, and Ollama at
http://localhost:11434.

To run the complete application stack in Docker instead:

```bash
./scripts/local_5090.sh up
./scripts/local_5090.sh status
```

Add `TAVILY_API_KEY` to `deploy/.env` only if the hosted fallback is wanted.
No hosted LLM API key is needed. `NVIDIA_API_KEY=ollama` is a compatibility
placeholder used by the LlamaIndex NVIDIA embedding client against Ollama's
local OpenAI-compatible endpoint.

## Health checks

```bash
curl -fsS http://localhost:11434/api/version
ollama ps
curl -fsS 'http://localhost:8888/search?q=NVIDIA&format=json'
curl -fsS http://localhost:8000/health
```

Test Qwen embeddings:

```bash
curl -fsS http://localhost:11434/v1/embeddings \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3-embedding:8b","input":["local research"]}'
```

## Operations

```bash
./scripts/local_5090.sh logs aiq-agent
./scripts/local_5090.sh down

# Inspect the single loaded model and its VRAM allocation.
ollama ps
nvidia-smi
```

Uploaded documents and reports persist in the `aiq-local-data` volume. Ollama
owns model persistence under its system service account.

## Privacy boundary

LLM inference, embeddings, reranking, uploaded documents, checkpoints, and
reports stay local. Web queries necessarily leave the machine:

- SearXNG sends them to its enabled public search engines.
- Tavily receives them only when the Tavily source is explicitly selected and
  `TAVILY_API_KEY` is configured.
