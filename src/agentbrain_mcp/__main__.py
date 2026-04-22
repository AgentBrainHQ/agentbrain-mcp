"""Entry point for `python -m agentbrain_mcp` and the `agentbrain-mcp` script.

Default transport is stdio (Claude Code, Cursor, Windsurf). Pass --http or --sse
to run over network transports for Claude Desktop Remote / ChatGPT connectors.
"""

from __future__ import annotations

import argparse
import sys

from .config import ConfigError
from .server import run_http, run_sse, run_stdio


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agentbrain-mcp",
        description="MCP server that exposes your Agent Brain to any MCP-capable AI client.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--stdio",
        action="store_true",
        help="Run over stdio (default). Use with Claude Code, Cursor, Windsurf.",
    )
    group.add_argument(
        "--http",
        action="store_true",
        help="Run over Streamable HTTP. Use with Claude Desktop Remote connectors.",
    )
    group.add_argument(
        "--sse",
        action="store_true",
        help="Run over legacy SSE transport (prefer --http for new deployments).",
    )
    parser.add_argument(
        "--mount-path",
        default=None,
        help="Optional mount path prefix when running behind a reverse proxy.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.http:
            run_http(mount_path=args.mount_path)
        elif args.sse:
            run_sse(mount_path=args.mount_path)
        else:
            run_stdio()
    except ConfigError as exc:
        print(f"[agentbrain-mcp] config error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
