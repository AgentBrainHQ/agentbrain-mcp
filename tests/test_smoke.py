"""Smoke tests — no network. Verify config + client construction + error shapes."""

from __future__ import annotations

import os

import pytest

from agentbrain_mcp.client import BrainAPIError, BrainClient
from agentbrain_mcp.config import Config, ConfigError


def test_config_requires_api_key(monkeypatch):
    monkeypatch.delenv("BRAIN_API_KEY", raising=False)
    monkeypatch.setenv("BRAIN_WORKSPACE_ID", "abc")
    with pytest.raises(ConfigError):
        Config.from_env()


def test_config_requires_workspace(monkeypatch):
    monkeypatch.setenv("BRAIN_API_KEY", "brain_xxx")
    monkeypatch.delenv("BRAIN_WORKSPACE_ID", raising=False)
    with pytest.raises(ConfigError):
        Config.from_env()


def test_config_defaults(monkeypatch):
    monkeypatch.setenv("BRAIN_API_KEY", "brain_xxx")
    monkeypatch.setenv("BRAIN_WORKSPACE_ID", "ws_xxx")
    monkeypatch.delenv("BRAIN_URL", raising=False)
    monkeypatch.delenv("BRAIN_TIMEOUT_S", raising=False)
    cfg = Config.from_env()
    assert cfg.api_key == "brain_xxx"
    assert cfg.workspace_id == "ws_xxx"
    assert cfg.brain_url == "https://api.agentbrain.ch"
    assert cfg.timeout_s == 45.0
    assert cfg.default_limit == 10


def test_config_strips_trailing_slash(monkeypatch):
    monkeypatch.setenv("BRAIN_API_KEY", "brain_xxx")
    monkeypatch.setenv("BRAIN_WORKSPACE_ID", "ws_xxx")
    monkeypatch.setenv("BRAIN_URL", "https://api.agentbrain.ch/")
    cfg = Config.from_env()
    assert cfg.brain_url == "https://api.agentbrain.ch"


def test_client_constructs_headers(monkeypatch):
    monkeypatch.setenv("BRAIN_API_KEY", "brain_test_key")
    monkeypatch.setenv("BRAIN_WORKSPACE_ID", "ws_test")
    client = BrainClient(Config.from_env())
    assert client._headers["X-API-Key"] == "brain_test_key"
    assert client._headers["Content-Type"] == "application/json"
    assert "agentbrain-mcp/" in client._headers["User-Agent"]


def test_brain_api_error_carries_status():
    err = BrainAPIError("boom", status=502, body="bad gateway")
    assert str(err) == "boom"
    assert err.status == 502
    assert err.body == "bad gateway"
