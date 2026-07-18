"""Tests for QualityEnforcer (rule-based and LLM-graded checks)."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from anvil.planning.models import QualityCheckResult, Step, StepResult, ToolCall
from anvil.quality.checks import no_tool_error, output_not_empty, file_exists
from anvil.quality.enforcer import QualityEnforcer


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def good_result():
    return StepResult(
        step_id="s1",
        tool_calls=[ToolCall(tool="echo_tool", input={"message": "hi"}, output="hi")],
        summary="hi",
        success=True,
    )


@pytest.fixture
def error_result():
    return StepResult(
        step_id="s1",
        success=False,
        exception="Something went wrong",
    )


@pytest.fixture
def empty_result():
    return StepResult(step_id="s1", success=True)


@pytest.fixture
def basic_step():
    return Step(step_id="s1", description="Echo something", tool_hint="echo_tool")


@pytest.fixture
def rubric_step():
    return Step(
        step_id="s1",
        description="Echo something",
        tool_hint="echo_tool",
        rubric="Output should contain the word 'hi'",
    )


# ── Rule check unit tests ──────────────────────────────────────────────────────

def test_no_tool_error_passes_on_success(good_result):
    passed, _ = no_tool_error(good_result)
    assert passed


def test_no_tool_error_fails_on_exception(error_result):
    passed, reason = no_tool_error(error_result)
    assert not passed
    assert "exception" in reason.lower()


def test_output_not_empty_passes_with_summary(good_result):
    passed, _ = output_not_empty(good_result)
    assert passed


def test_output_not_empty_fails_on_empty(empty_result):
    passed, reason = output_not_empty(empty_result)
    assert not passed


# ── QualityEnforcer integration tests ─────────────────────────────────────────

def test_enforcer_passes_good_result(good_result, basic_step):
    enforcer = QualityEnforcer()
    verdict = enforcer.check(basic_step, good_result)
    assert verdict.passed
    assert verdict.rule_check == "pass"
    assert verdict.llm_rubric_check is None  # No rubric set


def test_enforcer_fails_on_exception(error_result, basic_step):
    enforcer = QualityEnforcer()
    verdict = enforcer.check(basic_step, error_result)
    assert verdict.failed
    assert verdict.rule_check == "fail"


def test_enforcer_runs_rubric_if_set_and_passes(good_result, rubric_step):
    mock_client = MagicMock()
    import json
    mock_client.chat.return_value = json.dumps({"verdict": "pass", "reason": "Contains hi"})
    enforcer = QualityEnforcer(groq_client=mock_client)
    verdict = enforcer.check(rubric_step, good_result)
    assert verdict.passed
    assert verdict.llm_rubric_check == "pass"


def test_enforcer_runs_rubric_if_set_and_fails(good_result, rubric_step):
    mock_client = MagicMock()
    import json
    mock_client.chat.return_value = json.dumps({"verdict": "fail", "reason": "Missing word"})
    enforcer = QualityEnforcer(groq_client=mock_client)
    verdict = enforcer.check(rubric_step, good_result)
    assert verdict.failed
    assert verdict.llm_rubric_check == "fail"


def test_enforcer_skips_rubric_if_no_client(good_result, rubric_step):
    enforcer = QualityEnforcer(groq_client=None)
    verdict = enforcer.check(rubric_step, good_result)
    # Should pass rule checks, rubric check is skipped without a client.
    assert verdict.passed
    assert verdict.llm_rubric_check is None


def test_enforcer_custom_rule_registered(good_result, basic_step):
    def always_fail(result) -> tuple[bool, str]:
        return False, "Custom rule says no"

    enforcer = QualityEnforcer()
    enforcer.add_rule(always_fail)
    verdict = enforcer.check(basic_step, good_result)
    assert verdict.failed
    assert "Custom rule" in verdict.rule_failure_reason
