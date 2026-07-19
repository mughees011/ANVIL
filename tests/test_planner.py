"""Tests for Planner.generate_plan()."""

from __future__ import annotations

import json

import pytest

from anvil.planning.planner import Planner, PlannerError
from anvil.tools.registry import ToolRegistry, tool
from pydantic import BaseModel


class DummyParams(BaseModel):
    query: str


@tool(params_schema=DummyParams)
def example_tool(query: str) -> str:
    """Search the web for a query."""
    return f"Results for: {query}"


@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(example_tool)
    return reg


def test_generate_plan_returns_plan(mock_groq_plan, registry):
    planner = Planner(groq_client=mock_groq_plan)
    plan = planner.generate_plan(task="Do a thing", registry=registry)
    assert len(plan.steps) == 2
    assert plan.task == "Do a thing"


def test_generate_plan_step_fields(mock_groq_plan, registry):
    planner = Planner(groq_client=mock_groq_plan)
    plan = planner.generate_plan(task="Do a thing", registry=registry)
    step = plan.steps[0]
    assert step.description == "Search for information"
    assert step.tool_hint == "example_tool"
    assert step.status.value == "pending"


def test_generate_plan_malformed_raises(mock_groq_malformed, registry):
    planner = Planner(groq_client=mock_groq_malformed)
    with pytest.raises(PlannerError, match="non-JSON"):
        planner.generate_plan(task="Do a thing", registry=registry)


def test_generate_plan_missing_steps_key(registry):
    from unittest.mock import MagicMock
    client = MagicMock()
    client.chat.return_value = json.dumps({"not_steps": []})
    planner = Planner(groq_client=client)
    with pytest.raises(PlannerError, match="missing 'steps'"):
        planner.generate_plan(task="Do a thing", registry=registry)


def test_generate_plan_empty_steps_raises(registry):
    from unittest.mock import MagicMock
    client = MagicMock()
    client.chat.return_value = json.dumps({"steps": []})
    planner = Planner(groq_client=client)
    with pytest.raises(PlannerError, match="empty steps"):
        planner.generate_plan(task="Do a thing", registry=registry)


def test_generate_plan_strips_markdown_fences(registry):
    from unittest.mock import MagicMock
    plan_json = json.dumps({"steps": [{"id": "step_1", "description": "Step 1", "tool_hint": "", "depends_on": []}]})
    client = MagicMock()
    client.chat.return_value = f"```json\n{plan_json}\n```"
    planner = Planner(groq_client=client)
    plan = planner.generate_plan(task="Test", registry=registry)
    assert len(plan.steps) == 1
