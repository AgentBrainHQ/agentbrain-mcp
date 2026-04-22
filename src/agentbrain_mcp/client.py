"""Thin async HTTP client for the Agent Brain API.

Wraps /memory/recall, /memory/store, /memory/status with structured errors.
Single-responsibility: takes a Config, returns parsed dicts or raises BrainAPIError.
"""

from __future__ import annotations

from typing import Any

import httpx

from .config import Config


class BrainAPIError(RuntimeError):
    """Raised when the Brain API call fails in a way we want to surface upstream."""

    def __init__(self, message: str, *, status: int | None = None, body: str | None = None):
        super().__init__(message)
        self.status = status
        self.body = body


class BrainClient:
    def __init__(self, config: Config):
        self._config = config
        self._headers = {
            "Content-Type": "application/json",
            "X-API-Key": config.api_key,
            "User-Agent": "agentbrain-mcp/0.1.0",
        }

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._config.brain_url}{path}"
        async with httpx.AsyncClient(timeout=self._config.timeout_s) as http:
            try:
                resp = await http.post(url, json=payload, headers=self._headers)
            except httpx.TimeoutException as exc:
                raise BrainAPIError(f"Brain API timeout at {path}: {exc}") from exc
            except httpx.RequestError as exc:
                raise BrainAPIError(f"Brain API request failed at {path}: {exc}") from exc

        if resp.status_code >= 400:
            raise BrainAPIError(
                f"Brain API returned {resp.status_code} at {path}",
                status=resp.status_code,
                body=resp.text[:500],
            )

        try:
            return resp.json()
        except ValueError as exc:
            raise BrainAPIError(f"Brain API returned non-JSON at {path}: {exc}") from exc

    async def recall(self, query: str, limit: int | None = None) -> dict[str, Any]:
        payload = {
            "workspace_id": self._config.workspace_id,
            "query": query,
            "limit": limit or self._config.default_limit,
        }
        return await self._post("/memory/recall", payload)

    async def store(
        self,
        content: str,
        *,
        memory_type: str = "episodic",
        source_trust: float = 0.9,
    ) -> dict[str, Any]:
        payload = {
            "workspace_id": self._config.workspace_id,
            "content": content,
            "memory_type": memory_type,
            "source_trust": source_trust,
        }
        return await self._post("/memory/store", payload)

    async def status(self) -> dict[str, Any]:
        url = f"{self._config.brain_url}/health"
        async with httpx.AsyncClient(timeout=self._config.timeout_s) as http:
            try:
                resp = await http.get(url, headers=self._headers)
            except httpx.RequestError as exc:
                raise BrainAPIError(f"Brain API health check failed: {exc}") from exc
        if resp.status_code >= 400:
            raise BrainAPIError(
                f"Brain API /health returned {resp.status_code}",
                status=resp.status_code,
                body=resp.text[:500],
            )
        return resp.json()
