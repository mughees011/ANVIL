"""Tests for ToolRegistry and the @tool decorator."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from anvil.tools.registry import Tool, ToolRegistry, tool


# ── Fixtures ───────────────────────────────────────────────────────────────────

class EchoParams(BaseModel):
    message: str

class AddParams(BaseModel):
    a: int
    b: int


@tool(params_schema=EchoParams)
def echo_tool(message: str) -> str:
    """Echo a message back."""
    return message


@tool(params_schema=AddParams)
def add_tool(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_tool_decorator_sets_name():
    assert echo_tool.name == "echo_tool"


def test_tool_decorator_sets_description():
    assert "Echo a message" in echo_tool.description


def test_tool_decorator_custom_name():
    @tool(params_schema=EchoParams, name="my_custom_echo")
    def _fn(message: str) -> str:
        """Custom tool."""
        return message

    assert _fn.name == "my_custom_echo"


def test_tool_execute_validates_params():
    result = echo_tool.execute(message="hello")
    assert result == "hello"


def test_tool_execute_rejects_wrong_type():
    with pytest.raises(Exception):
        add_tool.execute(a="not_an_int", b=2)


def test_tool_to_groq_schema_shape():
    schema = echo_tool.to_groq_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "echo_tool"
    assert "parameters" in schema["function"]
    assert "properties" in schema["function"]["parameters"]
    assert "message" in schema["function"]["parameters"]["properties"]


def test_registry_register_and_get():
    registry = ToolRegistry()
    registry.register(echo_tool)
    assert registry.get("echo_tool") is echo_tool


def test_registry_collision_raises():
    registry = ToolRegistry()
    registry.register(echo_tool)
    with pytest.raises(ValueError, match="collision"):
        registry.register(echo_tool)


def test_registry_all_returns_all_tools():
    registry = ToolRegistry()
    registry.register(echo_tool)
    registry.register(add_tool)
    assert len(registry.all()) == 2


def test_registry_to_groq_schema_returns_list():
    registry = ToolRegistry()
    registry.register(echo_tool)
    registry.register(add_tool)
    schemas = registry.to_groq_schema()
    assert len(schemas) == 2
    assert all(s["type"] == "function" for s in schemas)


def test_registry_get_nonexistent_returns_none():
    registry = ToolRegistry()
    assert registry.get("nonexistent") is None


def test_registry_len():
    registry = ToolRegistry()
    assert len(registry) == 0
    registry.register(echo_tool)
    assert len(registry) == 1
