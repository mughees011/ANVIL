"""Tests for Executor (Phase 6)."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from anvil.execution.executor import Executor
from anvil.planning.models import Step
from anvil.tools.registry import ToolRegistry, tool


# Dummy tool for tests
class ExampleParams(BaseModel):
    message: str

@tool(params_schema=ExampleParams)
def example_tool(message: str) -> str:
    """An example tool."""
    return f"echo: {message}"

@tool(params_schema=ExampleParams)
def error_tool(message: str) -> str:
    """A tool that raises an exception."""
    raise ValueError(f"Intended error: {message}")


@pytest.fixture
def registry():
    r = ToolRegistry()
    r.register(example_tool)
    r.register(error_tool)
    return r


def test_executor_successful_tool_call(mock_groq_tool_call, registry, test_config):
    """Test executor successfully calls a tool returned by the LLM."""
    executor = Executor(
        groq_client=mock_groq_tool_call,
        registry=registry,
        config=test_config,
    )
    step = Step(step_id="step-1", description="Do something", tool_hint="example_tool")

    result = executor.run_step(step)

    assert result.success is True
    assert len(result.tool_calls) == 1
    tc = result.tool_calls[0]
    assert tc.tool == "example_tool"
    assert tc.input == {"message": "hello from test"}
    assert tc.output == "echo: hello from test"
    assert "echo: hello from test" in result.summary


def test_executor_no_tool_call(mock_groq_no_tool, registry, test_config):
    """Test executor handles plain text response from LLM."""
    executor = Executor(
        groq_client=mock_groq_no_tool,
        registry=registry,
        config=test_config,
    )
    step = Step(step_id="step-2", description="Just talk")

    result = executor.run_step(step)

    assert result.success is True
    assert len(result.tool_calls) == 0
    assert result.summary == "No tool needed, done."


def test_executor_tool_not_found_in_registry_hint(mock_groq_tool_call, registry, test_config):
    """Test executor fails early if step.tool_hint doesn't exist."""
    executor = Executor(
        groq_client=mock_groq_tool_call,
        registry=registry,
        config=test_config,
    )
    step = Step(step_id="step-3", description="Use hallucinated tool", tool_hint="made_up_tool")

    result = executor.run_step(step)

    assert result.success is False
    assert "not found in registry" in result.exception
    # Groq client should not even be called if tool_hint is invalid
    mock_groq_tool_call.chat_with_tools.assert_not_called()


def test_executor_tool_execution_exception(mock_groq_tool_call, registry, test_config):
    """Test executor handles exceptions raised by the tool function itself."""
    # We mock the groq client to call 'error_tool'
    import json
    from unittest.mock import MagicMock
    
    tc_mock = MagicMock()
    tc_mock.function.name = "error_tool"
    tc_mock.function.arguments = json.dumps({"message": "fail me"})
    
    msg_mock = MagicMock()
    msg_mock.content = None
    msg_mock.tool_calls = [tc_mock]
    
    mock_client = MagicMock()
    mock_client.chat_with_tools.return_value = msg_mock
    
    executor = Executor(
        groq_client=mock_client,
        registry=registry,
        config=test_config,
    )
    step = Step(step_id="step-4", description="Cause an error")
    
    result = executor.run_step(step)
    
    assert result.success is False
    assert "Intended error: fail me" in result.exception
    assert len(result.tool_calls) == 0
