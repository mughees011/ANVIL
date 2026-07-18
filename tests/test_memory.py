"""Tests for MemoryStore (ChromaDB-backed)."""

from __future__ import annotations

import pytest

from anvil.memory.store import MemoryStore


@pytest.fixture
def store(tmp_path):
    """MemoryStore backed by a temp directory — never touches .anvil/chroma/."""
    return MemoryStore(agent_name="test_agent", chroma_path=tmp_path / "chroma")


def test_remember_and_recall_episodic(store):
    store.remember("The sky is blue", collection="episodic", run_id="r1", step_id="s1")
    hits = store.recall("blue sky", k=5, collection="episodic")
    assert len(hits) == 1
    assert "blue" in hits[0].document


def test_remember_and_recall_semantic(store):
    store.remember("Python was created by Guido", collection="semantic")
    hits = store.recall("Guido Python", k=5, collection="semantic")
    assert len(hits) == 1


def test_recall_both_collections(store):
    store.remember("fact A", collection="episodic", run_id="r1")
    store.remember("fact B", collection="semantic")
    hits = store.recall("fact", k=5, collection="both")
    assert len(hits) == 2


def test_recall_empty_returns_empty(store):
    hits = store.recall("anything", k=5, collection="both")
    assert hits == []


def test_recall_top_k_respected(store):
    for i in range(5):
        store.remember(f"memory fragment {i}", collection="episodic", run_id="r1")
    hits = store.recall("memory fragment", k=3, collection="episodic")
    assert len(hits) <= 3


def test_clear_episodic(store):
    store.remember("ephemeral", collection="episodic", run_id="r1")
    store.clear_episodic()
    hits = store.recall("ephemeral", k=5, collection="episodic")
    assert hits == []


def test_clear_episodic_does_not_affect_semantic(store):
    store.remember("permanent fact", collection="semantic")
    store.remember("temporary fact", collection="episodic", run_id="r1")
    store.clear_episodic()
    hits = store.recall("permanent", k=5, collection="semantic")
    assert len(hits) == 1


def test_metadata_stored_correctly(store):
    store.remember("test doc", collection="episodic", run_id="run-42", step_id="step-1")
    hits = store.recall("test doc", k=1, collection="episodic")
    assert hits[0].metadata.get("run_id") == "run-42"
    assert hits[0].metadata.get("step_id") == "step-1"
    assert hits[0].metadata.get("memory_type") == "episodic"
