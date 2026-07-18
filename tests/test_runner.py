"""Tests for AgentRunner (Phase 9)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from anvil.agent import AgentRunner
def _make_tool_call_message(tool_name: str, args: dict) -> MagicMock:
    tc = MagicMock()
    tc.function.name = tool_name
    tc.function.arguments = json.dumps(args)
    msg = MagicMock()
    msg.content = None
    msg.tool_calls = [tc]
    return msg


def test_runner_end_to_end_success(mocker, test_config):
    """Test a full run of AgentRunner with mocked success."""
    # 1. Mock GroqClient.chat for Planner (returns 1 step plan)
    plan_json = json.dumps({
        "steps": [
            {
                "description": "Step 1: Get info",
                "tool_hint": "example_tool",
                "depends_on": [],
                "rubric": None,
            }
        ]
    })
    
    chat_mock = mocker.patch("anvil.llm.groq_client.GroqClient.chat")
    chat_mock.return_value = plan_json
    
    # 2. Mock GroqClient.chat_with_tools for Executor (returns a tool call)
    chat_with_tools_mock = mocker.patch("anvil.llm.groq_client.GroqClient.chat_with_tools")
    chat_with_tools_mock.return_value = _make_tool_call_message(
        tool_name="example_tool",
        args={"message": "success!"}
    )
    
    # 3. Dummy tool
    from anvil.tools.registry import ToolRegistry, tool
    from pydantic import BaseModel
    class Params(BaseModel):
        message: str
    @tool(params_schema=Params)
    def example_tool(message: str) -> str:
        return "done"
    
    # Run
    runner = AgentRunner(config=test_config, tools=[example_tool], verbose=False)
    result = runner.run("Do the task")
    
    assert result.status == "success"
    assert result.output_summary == "Step 1: Get info"
    assert "trace_path" in result.model_dump()


def test_runner_with_self_healing(mocker, test_config):
    """Test that self-healing handles a failure correctly (re-plan or retry)."""
    # Planner returns 1 step plan
    plan_json = json.dumps({
        "steps": [
            {
                "description": "Step 1: Flaky step",
                "tool_hint": "flaky_tool",
                "depends_on": [],
                "rubric": None,
            }
        ]
    })
    
    chat_mock = mocker.patch("anvil.llm.groq_client.GroqClient.chat")
    # chat is called by planner initially, then by Quality/Healer maybe? 
    # For now, just return plan_json for all generic chat calls.
    # Self healer re-planning uses chat, Quality enforcer uses chat. 
    # Let's provide a side_effect to distinguish calls if necessary, but returning plan_json
    # might fail if parsed as quality rubric. Wait, we don't have a rubric, so quality check skips LLM.
    chat_mock.return_value = plan_json
    
    chat_with_tools_mock = mocker.patch("anvil.llm.groq_client.GroqClient.chat_with_tools")
    
    # Side effect: first call returns a non-existent tool call to cause an error
    # second call returns a valid one
    call_1 = _make_tool_call_message(tool_name="bad_tool", args={})
    call_2 = _make_tool_call_message(tool_name="flaky_tool", args={"message": "ok"})
    chat_with_tools_mock.side_effect = [call_1, call_2]
    
    # Dummy tool
    from anvil.tools.registry import tool
    from pydantic import BaseModel
    class Params(BaseModel):
        message: str
    @tool(params_schema=Params)
    def flaky_tool(message: str) -> str:
        return "worked"
    
    test_config.max_retries = 3
    runner = AgentRunner(config=test_config, tools=[flaky_tool], verbose=False)
    
    result = runner.run("Try until you succeed")
    
    # Should succeed on the second attempt
    assert result.status == "success"
    # Executor should be called twice
    assert chat_with_tools_mock.call_count == 2
