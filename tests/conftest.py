"""Shared pytest fixtures.

Per TRD §11: all Groq API calls must be mocked in tests — no test
may require a live GROQ_API_KEY.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from anvil.config import AgentConfig
from anvil.llm.groq_client import GroqClient


# ── AgentConfig fixture ────────────────────────────────────────────────────────

@pytest.fixture
def test_config(tmp_path) -> AgentConfig:
    """Minimal AgentConfig for tests — no real YAML file needed."""
    cfg = AgentConfig(
        name="test_agent",
        planner_model="llama-3.3-70b-versatile",
        executor_model="llama-3.3-70b-versatile",
        max_retries=2,
        memory_top_k=3,
    )
    cfg.groq_api_key = "test-key-not-real"
    return cfg


# ── Mocked Groq response helpers ───────────────────────────────────────────────

def _make_chat_message(content: str) -> MagicMock:
    """Return a mock Groq chat response with the given text content."""
    msg = MagicMock()
    msg.content = content
    msg.tool_calls = None
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _make_tool_call_message(tool_name: str, args: dict) -> MagicMock:
    """Return a mock Groq message that contains a tool call."""
    tc = MagicMock()
    tc.function.name = tool_name
    tc.function.arguments = json.dumps(args)

    msg = MagicMock()
    msg.content = None
    msg.tool_calls = [tc]
    return msg


# ── GroqClient mock fixtures ───────────────────────────────────────────────────

@pytest.fixture
def mock_groq_plan():
    """GroqClient.chat() returns a valid 2-step plan JSON."""
    plan_json = json.dumps({
        "steps": [
            {
                "description": "Search for information",
                "tool_hint": "example_tool",
                "depends_on": [],
                "rubric": None,
            },
            {
                "description": "Synthesise the result",
                "tool_hint": "",
                "depends_on": [],
                "rubric": None,
            },
        ]
    })
    client = MagicMock(spec=GroqClient)
    client.chat.return_value = plan_json
    return client


@pytest.fixture
def mock_groq_malformed():
    """GroqClient.chat() returns unparseable text."""
    client = MagicMock(spec=GroqClient)
    client.chat.return_value = "sorry, I cannot produce a plan today"
    return client


@pytest.fixture
def mock_groq_tool_call():
    """GroqClient.chat_with_tools() returns a tool call for 'example_tool'."""
    client = MagicMock(spec=GroqClient)
    client.chat_with_tools.return_value = _make_tool_call_message(
        tool_name="example_tool",
        args={"message": "hello from test"},
    )
    return client


@pytest.fixture
def mock_groq_no_tool():
    """GroqClient.chat_with_tools() returns a plain text response (no tool call)."""
    client = MagicMock(spec=GroqClient)
    msg = MagicMock()
    msg.content = "No tool needed, done."
    msg.tool_calls = None
    client.chat_with_tools.return_value = msg
    return client
