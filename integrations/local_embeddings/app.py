import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastembed import TextEmbedding
from pydantic import BaseModel

MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
_model: TextEmbedding | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _model
    _model = TextEmbedding(model_name=MODEL_NAME)
    yield


app = FastAPI(title="Local OpenAI-compatible embeddings", lifespan=lifespan)


class EmbeddingRequest(BaseModel):
    input: str | list[str]
    model: str | None = None
    input_type: str | None = None
    encoding_format: str | None = None
    truncate: str | None = None


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model": MODEL_NAME, "ready": _model is not None}


@app.get("/v1/models")
def models() -> dict[str, Any]:
    return {"object": "list", "data": [{"id": MODEL_NAME, "object": "model", "owned_by": "local"}]}


@app.post("/v1/embeddings")
def embeddings(request: EmbeddingRequest) -> dict[str, Any]:
    if _model is None:
        raise RuntimeError("Embedding model is not ready")

    texts = [request.input] if isinstance(request.input, str) else request.input
    vectors = [vector.tolist() for vector in _model.embed(texts)]
    return {
        "object": "list",
        "model": MODEL_NAME,
        "data": [{"object": "embedding", "index": index, "embedding": vector} for index, vector in enumerate(vectors)],
        "usage": {
            "prompt_tokens": sum(len(text.split()) for text in texts),
            "total_tokens": sum(len(text.split()) for text in texts),
        },
    }
