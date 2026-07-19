"""Tests for AgentConfig loading and environment resolution."""

import os
from pathlib import Path
import pytest
from anvil.config import load_config, ConfigError

def test_load_config_finds_env_in_parent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that load_config finds .env when called from a subdirectory (find_dotenv upward search)."""
    
    # 1. Setup a directory structure:
    # tmp_path/
    # ├── .env                 <-- contains GROQ_API_KEY
    # └── examples/
    #     └── my_agent/
    #         └── anvil.config.yaml
    
    root_dir = tmp_path
    env_file = root_dir / ".env"
    env_file.write_text("GROQ_API_KEY=test_upward_key\n")
    
    agent_dir = root_dir / "examples" / "my_agent"
    agent_dir.mkdir(parents=True)
    
    config_file = agent_dir / "anvil.config.yaml"
    config_file.write_text("name: test_agent\n")
    
    # Clear out the env var so we ensure it's loaded from the .env file
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    
    # 2. Change working directory to the sub-folder
    monkeypatch.chdir(agent_dir)
    
    # 3. Call load_config using default dotenv_path=".env"
    # It should walk up from CWD, find root_dir/.env, and load the key.
    config = load_config(config_path="anvil.config.yaml")
    
    assert config.groq_api_key == "test_upward_key"
    assert config.name == "test_agent"


def test_load_config_respects_explicit_dotenv_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that explicit dotenv_path is respected and not overridden by upward search."""
    root_dir = tmp_path
    
    # Put a specific env file somewhere else
    custom_env = root_dir / "custom.env"
    custom_env.write_text("GROQ_API_KEY=explicit_key\n")
    
    config_file = root_dir / "anvil.config.yaml"
    config_file.write_text("name: test_agent\n")
    
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.chdir(root_dir)
    
    config = load_config(config_path="anvil.config.yaml", dotenv_path="custom.env")
    
    assert config.groq_api_key == "explicit_key"
