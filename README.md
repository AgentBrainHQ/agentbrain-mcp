# agentbrain-mcp

MCP server that gives any MCP-capable AI client (Claude Code, Claude Desktop, Cursor, Windsurf) access to your personal Agent Brain — cross-source memory that persists across tools, conversations, and devices.

Status: [status.agentbrain.ch](https://status.agentbrain.ch) · Changelog: [CHANGELOG.md](./CHANGELOG.md) · License: MIT

## What it does

Three tools, registered as native MCP tools:

- **`brain_recall(query, limit)`** — search your Brain for relevant memories
- **`brain_store(content, memory_type, source_trust)`** — persist a memory
- **`brain_status()`** — health check

The server is single-user: each install is bound to one workspace via env vars. If you have multiple brains (work/personal), run multiple instances.

## Install

```bash
pip install agentbrain-mcp
```

Or from source:

```bash
git clone https://github.com/AgentBrainHQ/agentbrain-mcp
cd agentbrain-mcp
pip install -e .
```

## Configure

Get your API key and workspace id from <https://agentbrain.ch/settings>. Export them:

```bash
export BRAIN_API_KEY='brain_xxxxxxxxxxxx'
export BRAIN_WORKSPACE_ID='xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
```

Optional:

| Env var | Default | Purpose |
|---|---|---|
| `BRAIN_URL` | `https://api.agentbrain.ch` | Brain API base URL (override for self-hosted) |
| `BRAIN_TIMEOUT_S` | `45` | Request timeout in seconds |
| `BRAIN_DEFAULT_LIMIT` | `10` | Default `limit` for `brain_recall` when not provided |

## Use with Claude Code

```bash
claude mcp add agentbrain --scope user \
  -e BRAIN_API_KEY=$BRAIN_API_KEY \
  -e BRAIN_WORKSPACE_ID=$BRAIN_WORKSPACE_ID \
  -- agentbrain-mcp
```

Then in any Claude Code session:

```
> brain_recall("previous decisions on auth")
```

## Use with Cursor / Windsurf

Add to your MCP config (`~/.cursor/mcp.json` or equivalent):

```json
{
  "mcpServers": {
    "agentbrain": {
      "command": "agentbrain-mcp",
      "env": {
        "BRAIN_API_KEY": "brain_xxxxxxxxxxxx",
        "BRAIN_WORKSPACE_ID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      }
    }
  }
}
```

## Use with Claude Desktop

Same JSON as Cursor, in `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows).

## Test it runs

```bash
# Should print a config error if env not set — no network required
agentbrain-mcp
```

With env set it will wait for an MCP client to connect on stdio.

## Run over HTTP / SSE

For Claude Desktop Remote Connectors or a self-hosted endpoint:

```bash
# Streamable HTTP (recommended for new deployments)
agentbrain-mcp --http

# Legacy SSE
agentbrain-mcp --sse
```

Single-tenant: the endpoint is bound to the API key and workspace id of the process that started it. Host behind your own reverse proxy (Traefik, Caddy, nginx) for TLS. Multi-tenant hosting (one endpoint, many users with different keys) requires a separate server and is not in scope here.

## Development

```bash
pip install -e ".[dev]"
pytest
```

Build the package:

```bash
pip install build twine
python -m build
twine check dist/*
```

## License

MIT — see [LICENSE](./LICENSE).
