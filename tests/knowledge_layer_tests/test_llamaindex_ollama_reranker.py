from types import SimpleNamespace

import pytest
from knowledge_layer.llamaindex.adapter import LlamaIndexRetriever


class _FakeResponse:
    def __init__(self, answer: str):
        self._answer = answer

    def raise_for_status(self):
        return None

    def json(self):
        return {"response": self._answer}


class _FakeClient:
    def __init__(self, answers: list[str]):
        self._answers = iter(answers)
        self.requests: list[dict] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def post(self, _url: str, json: dict):
        self.requests.append(json)
        if "prompt" not in json:
            return _FakeResponse("")
        return _FakeResponse(next(self._answers))


@pytest.mark.asyncio
async def test_ollama_reranker_prioritizes_relevant_nodes_and_unloads(monkeypatch):
    client = _FakeClient(["no", "yes", "yes"])
    monkeypatch.setattr(
        "knowledge_layer.llamaindex.adapter.httpx.AsyncClient",
        lambda **_: client,
    )

    retriever = LlamaIndexRetriever.__new__(LlamaIndexRetriever)
    retriever.reranker_model = "qwen-reranker"
    retriever.reranker_base_url = "http://ollama:11434"
    nodes = [
        SimpleNamespace(node=SimpleNamespace(get_content=lambda: "first")),
        SimpleNamespace(node=SimpleNamespace(get_content=lambda: "second")),
        SimpleNamespace(node=SimpleNamespace(get_content=lambda: "third")),
    ]

    result = await retriever._rerank("query", nodes, top_k=2)

    assert result == nodes[1:]
    assert client.requests[-1] == {
        "model": "qwen-reranker",
        "keep_alive": 0,
    }


def test_qwen_reranker_prompt_uses_documented_contract():
    prompt = LlamaIndexRetriever._reranker_prompt("capital?", "Paris")

    assert 'answer can only be "yes" or "no"' in prompt
    assert "<Query>: capital?" in prompt
    assert "<Document>: Paris" in prompt
