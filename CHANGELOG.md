# Changelog

All notable changes to `agentbrain-mcp` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [SemVer](https://semver.org/).

## [0.1.0] — 2026-04-22

Initial release.

### Added
- `brain_recall(query, limit)` — semantic search over your Agent Brain memory
- `brain_store(content, memory_type, source_trust)` — persist memory with structured tags
- `brain_status()` — health check of Brain API + workspace
- stdio transport (Claude Code, Cursor, Windsurf, Claude Desktop local config)
- Streamable-HTTP transport (`--http`) for Claude Desktop Remote Connectors
- Legacy SSE transport (`--sse`) for older MCP clients
- Structured error responses (`{ok: false, error, status, body}`) instead of stack traces
- Configurable via env vars: `BRAIN_API_KEY`, `BRAIN_WORKSPACE_ID`, `BRAIN_URL`, `BRAIN_TIMEOUT_S`, `BRAIN_DEFAULT_LIMIT`
- Fail-fast config validation (exit code 2 on missing keys)
- 6 smoke tests covering config + client + error shapes

### Design decisions
- **Single-user by design:** one instance = one workspace. Multi-tenant hosting is a separate server (out of scope).
- **Bound at startup:** API key + workspace ID are validated once, reused for all requests. Key rotation requires restart.
- **No local caching:** every tool call hits Brain API. Simpler, more debuggable, latency acceptable.
