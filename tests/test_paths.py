"""Tests for path resolution (anchoring to project root)."""

import json
from pathlib import Path
import pytest

from anvil.config import get_project_root
from anvil.tracing.trace import RunTrace
from anvil.memory.store import MemoryStore

def test_get_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that get_project_root finds pyproject.toml upward."""
    root_dir = tmp_path
    (root_dir / "pyproject.toml").write_text("[project]\nname = 'test'")
    
    sub_dir = root_dir / "nested" / "deep"
    sub_dir.mkdir(parents=True)
    
    monkeypatch.chdir(sub_dir)
    
    resolved_root = get_project_root()
    assert resolved_root == root_dir

def test_memory_store_uses_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that MemoryStore uses project root when no explicit path is given."""
    root_dir = tmp_path
    (root_dir / "pyproject.toml").write_text("[project]\nname = 'test'")
    sub_dir = root_dir / "sub"
    sub_dir.mkdir(parents=True)
    monkeypatch.chdir(sub_dir)
    
    store = MemoryStore("test_agent")
    
    expected_path = root_dir / ".anvil" / "chroma"
    assert expected_path.exists()

def test_trace_uses_project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that RunTrace writes to project root."""
    root_dir = tmp_path
    (root_dir / "pyproject.toml").write_text("[project]\nname = 'test'")
    sub_dir = root_dir / "sub"
    sub_dir.mkdir(parents=True)
    monkeypatch.chdir(sub_dir)
    
    trace = RunTrace(agent_name="test_agent", task="test task", verbose=False)
    trace_path = trace.finalize(final_status="success")
    
    assert trace_path.parent == root_dir / ".anvil" / "runs"
    assert trace_path.exists()
