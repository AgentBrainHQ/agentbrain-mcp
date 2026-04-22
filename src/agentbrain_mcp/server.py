"""FastMCP server exposing three tools: brain_recall, brain_store, brain_status.

Single-user design: server is bound to one workspace via env vars at startup.
Errors from the Brain API are returned as structured dicts so the LLM can reason
about failures instead of getting a raw stack trace.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import BrainAPIError, BrainClient
from .config import Config

mcp = FastMCP("agentbrain")

_client: BrainClient | None = None


def _get_client() -> BrainClient:
    global _client
    if _client is None:
        _client = BrainClient(Config.from_env())
    return _client


def _error_payload(exc: BrainAPIError) -> dict[str, Any]:
    return {
        "ok": False,
        "error": str(exc),
        "status": exc.status,
        "body": exc.body,
    }


@mcp.tool()
async def brain_recall(query: str, limit: int = 10) -> dict[str, Any]:
    """Search your Agent Brain for memories relevant to a query.

    Use this BEFORE starting a non-trivial task to load prior context, decisions,
    and learnings. Returns ranked memories with content, type, and timestamps.

    Args:
        query: A description of what you need to know. More specific = better ranking.
        limit: Max memories to return (1-50, default 10).
    """
    if not query or not query.strip():
        return {"ok": False, "error": "query must be a non-empty string"}
    limit = max(1, min(int(limit), 50))
    try:
        data = await _get_client().recall(query.strip(), limit=limit)
        return {"ok": True, "data": data}
    except BrainAPIError as exc:
        return _error_payload(exc)


@mcp.tool()
async def brain_store(
    content: str,
    memory_type: str = "episodic",
    source_trust: float = 0.9,
) -> dict[str, Any]:
    """Store a memory in your Agent Brain.

    Call this AFTER completing a task, making a decision, or learning something
    important. The Brain will extract entities, link them to your knowledge graph,
    and consolidate during the next dream cycle.

    Args:
        content: The memory text. Use structured tags for retrievability, e.g.
            "[DATE:2026-04-22] [TYPE:Decision] Chose FastMCP over raw SDK because ..."
        memory_type: One of "episodic" (events, default), "semantic" (facts),
            "procedural" (how-to patterns).
        source_trust: 0.0-1.0 confidence. 0.9 verified facts, 0.7 observations.
    """
    if not content or not content.strip():
        return {"ok": False, "error": "content must be a non-empty string"}
    if memory_type not in {"episodic", "semantic", "procedural"}:
        return {
            "ok": False,
            "error": f"memory_type must be episodic|semantic|procedural, got: {memory_type}",
        }
    source_trust = max(0.0, min(float(source_trust), 1.0))
    try:
        data = await _get_client().store(
            content.strip(),
            memory_type=memory_type,
            source_trust=source_trust,
        )
        return {"ok": True, "data": data}
    except BrainAPIError as exc:
        return _error_payload(exc)


@mcp.tool()
async def brain_status() -> dict[str, Any]:
    """Check Agent Brain API health and your workspace status.

    Use this if recall or store is failing and you need to diagnose whether
    the issue is the API, the network, or your config.
    """
    try:
        data = await _get_client().status()
        return {"ok": True, "data": data}
    except BrainAPIError as exc:
        return _error_payload(exc)


def run_stdio() -> None:
    """Start the MCP server over stdio (Claude Code, Cursor, Windsurf)."""
    _get_client()  # fail fast on bad config before launching transport
    mcp.run(transport="stdio")


def run_http(mount_path: str | None = None) -> None:
    """Start the MCP server over Streamable HTTP (Claude Desktop Remote, ChatGPT Connectors).

    Single-tenant: the API key and workspace id come from env vars at startup.
    For self-hosted deployments behind your own reverse proxy. Multi-tenant
    hosting (one endpoint, many users) is a separate server that is not in
    scope here.
    """
    _get_client()
    mcp.run(transport="streamable-http", mount_path=mount_path)


def run_sse(mount_path: str | None = None) -> None:
    """Start the MCP server over the legacy SSE transport.

    Kept for clients that have not moved to Streamable HTTP yet. Prefer
    `run_http()` for new deployments.
    """
    _get_client()
    mcp.run(transport="sse", mount_path=mount_path)
