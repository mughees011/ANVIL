"""AgentConfig — Pydantic model matching anvil.config.yaml.

Exact schema: docs/planning/05_BACKEND_SCHEMA_ANVIL.md §3.
Loads from YAML + resolves GROQ_API_KEY from .env per §5
(constructor param > env var > raise ConfigError, never silent).
"""

# TODO (Phase 0/3): implement AgentConfig, ConfigError, load_config()
