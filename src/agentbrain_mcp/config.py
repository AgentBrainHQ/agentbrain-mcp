"""Configuration loading from environment variables.

Single-user model: each MCP-Server install is bound to one workspace via env vars.
No config-file reading, no secrets on disk. If vars missing, we raise early.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    """Raised when required config is missing or invalid."""


@dataclass(frozen=True)
class Config:
    api_key: str
    workspace_id: str
    brain_url: str
    timeout_s: float
    default_limit: int

    @classmethod
    def from_env(cls) -> "Config":
        api_key = os.environ.get("BRAIN_API_KEY", "").strip()
        workspace_id = os.environ.get("BRAIN_WORKSPACE_ID", "").strip()

        if not api_key:
            raise ConfigError(
                "BRAIN_API_KEY is not set. Get your key at https://agentbrain.ch/settings "
                "and set it before running this MCP server."
            )
        if not workspace_id:
            raise ConfigError(
                "BRAIN_WORKSPACE_ID is not set. Find your workspace id in "
                "https://agentbrain.ch/settings and export it before running."
            )

        brain_url = os.environ.get("BRAIN_URL", "https://api.agentbrain.ch").rstrip("/")

        try:
            timeout_s = float(os.environ.get("BRAIN_TIMEOUT_S", "45"))
        except ValueError as exc:
            raise ConfigError(f"BRAIN_TIMEOUT_S must be a number, got: {exc}") from exc

        try:
            default_limit = int(os.environ.get("BRAIN_DEFAULT_LIMIT", "10"))
        except ValueError as exc:
            raise ConfigError(f"BRAIN_DEFAULT_LIMIT must be an integer, got: {exc}") from exc

        return cls(
            api_key=api_key,
            workspace_id=workspace_id,
            brain_url=brain_url,
            timeout_s=timeout_s,
            default_limit=default_limit,
        )
