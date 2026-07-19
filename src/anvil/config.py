"""AgentConfig — Pydantic model matching anvil.config.yaml.

Exact schema: docs/planning/05_BACKEND_SCHEMA_ANVIL.md §3.
Loads from YAML + resolves GROQ_API_KEY from .env per §5
(constructor param > env var > raise ConfigError, never silent).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator


class ConfigError(Exception):
    """Raised for missing or invalid configuration — fails fast before any API call."""


class AgentConfig(BaseModel):
    name: str
    planner_model: str = "llama-3.3-70b-versatile"
    executor_model: str = "llama-3.3-70b-versatile"
    max_retries: int = Field(default=3, ge=0)
    memory_top_k: int = Field(default=5, ge=1)
    halt_on_failure: bool = True
    allow_shell_tool: bool = False
    shell_jail_dir: Optional[Path] = None
    shell_timeout_seconds: int = Field(default=30, ge=1)

    # Resolved at load time — never written to disk or traces.
    groq_api_key: str = Field(default="", exclude=True, repr=False)

    @model_validator(mode="after")
    def _validate_shell_config(self) -> "AgentConfig":
        if self.allow_shell_tool and not self.shell_jail_dir:
            raise ConfigError(
                "allow_shell_tool=true requires shell_jail_dir to be set. "
                "Refusing to run shell commands without an explicit jail directory."
            )
        return self


def load_config(
    config_path: str | Path,
    *,
    groq_api_key: Optional[str] = None,
    dotenv_path: str | Path = ".env",
) -> AgentConfig:
    """Load AgentConfig from a YAML file, resolving the Groq API key.

    Resolution order for GROQ_API_KEY:
      1. Explicit `groq_api_key` constructor param (mainly for tests).
      2. GROQ_API_KEY environment variable (loaded from dotenv_path first).
      3. If neither is present: raise ConfigError immediately.

    Args:
        config_path: Path to anvil.config.yaml.
        groq_api_key: Optional explicit key (overrides env var).
        dotenv_path: Path to .env file (loaded before env var lookup).

    Returns:
        Validated AgentConfig instance with groq_api_key populated.

    Raises:
        ConfigError: If config file is missing, YAML is invalid,
                     Pydantic validation fails, or API key is absent.
    """
    from dotenv import load_dotenv, find_dotenv

    if str(dotenv_path) == ".env":
        resolved_dotenv_path = find_dotenv(usecwd=True)
    else:
        resolved_dotenv_path = str(dotenv_path)

    load_dotenv(dotenv_path=resolved_dotenv_path, override=False)

    config_path = Path(config_path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {config_path}: {exc}") from exc

    try:
        config = AgentConfig(**raw)
    except Exception as exc:
        raise ConfigError(f"Config validation failed: {exc}") from exc

    # Resolve the API key.
    resolved_key = groq_api_key or os.environ.get("GROQ_API_KEY", "")
    if not resolved_key:
        raise ConfigError(
            "GROQ_API_KEY is not set. Add it to your .env file or pass it explicitly."
        )
    config.groq_api_key = resolved_key

    return config
