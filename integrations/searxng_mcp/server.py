import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://searxng:8080").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("SEARXNG_TIMEOUT_SECONDS", "30"))

mcp = FastMCP(
    "Local SearXNG Web Search",
    host="0.0.0.0",
    port=9901,
    stateless_http=True,
)


@mcp.tool()
async def search_web(query: str, max_results: int = 8) -> list[dict[str, Any]]:
    """Search the public web and return citation-ready sources."""
    limit = max(1, min(max_results, 15))
    params = {
        "q": query,
        "format": "json",
        "language": "en",
        "safesearch": 1,
    }
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        response = await client.get(f"{SEARXNG_URL}/search", params=params)
        response.raise_for_status()
        payload = response.json()

    normalized: list[dict[str, Any]] = []
    for result in payload.get("results", [])[:limit]:
        url = result.get("url")
        if not url:
            continue
        normalized.append(
            {
                "title": result.get("title") or url,
                "url": url,
                "snippet": result.get("content") or "",
                "published_date": result.get("publishedDate"),
                "engine": result.get("engine"),
                "score": result.get("score"),
            }
        )
    return normalized


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
