"""Tests for SelfHealingEngine (retry counting + halt behavior)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from anvil.config import AgentConfig
from anvil.healing.self_heal import SelfHealingEngine
from anvil.planning.models import Plan, Step, StepResult, StepStatus
from anvil.quality.enforcer import QualityVerdict


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_config(max_retries=2, halt=True) -> AgentConfig:
    cfg = AgentConfig(name="test_agent", max_retries=max_retries, halt_on_failure=halt)
    cfg.groq_api_key = "test"
    return cfg


def _exception_verdict():
    return QualityVerdict(passed=False, rule_check="fail", rule_failure_reason="Tool raised an exception: boom")


def _rubric_verdict():
    return QualityVerdict(
        passed=False,
        rule_check="pass",
        llm_rubric_check="fail",
        llm_rubric_reason="Output didn't satisfy rubric",
    )


def _make_plan() -> Plan:
    return Plan(task="test task", steps=[
        Step(description="Step A", tool_hint="echo_tool"),
        Step(description="Step B", tool_hint=""),
    ])


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_same_step_retry_on_exception():
    """Exception failures should trigger same-step retry, not re-plan."""
    config = _make_config(max_retries=2)
    healer = SelfHealingEngine(config)
    step = Step(description="Do something", tool_hint="t", retry_count=0)
    result = StepResult(step_id=step.step_id, success=False, exception="boom")
    plan = Plan(task="t", steps=[step])

    healing = healer.handle_failure(
        step=step, result=result, verdict=_exception_verdict(),
        executor=MagicMock(), planner=MagicMock(), plan=plan, registry=MagicMock(),
    )

    assert healing.should_retry
    assert not healing.abort
    assert step.status == StepStatus.RETRIED


def test_partial_replan_on_rubric_failure():
    """Quality/rubric failures should trigger a partial re-plan."""
    config = _make_config(max_retries=2)
    healer = SelfHealingEngine(config)
    step = Step(description="Do something", tool_hint="t", retry_count=0, rubric="be correct")
    result = StepResult(step_id=step.step_id, success=True, summary="wrong output")
    plan = Plan(task="t", steps=[step])

    mock_planner = MagicMock()
    mock_planner.generate_plan.return_value = Plan(
        task="re-plan", steps=[Step(description="Revised step", tool_hint="")]
    )

    healing = healer.handle_failure(
        step=step, result=result, verdict=_rubric_verdict(),
        executor=MagicMock(), planner=mock_planner, plan=plan, registry=MagicMock(),
    )

    assert healing.should_retry
    assert not healing.abort
    mock_planner.generate_plan.assert_called_once()


def test_abort_on_max_retries_exceeded():
    """When retry_count >= max_retries, should abort and mark step FAILED."""
    config = _make_config(max_retries=2)
    healer = SelfHealingEngine(config)
    # Already at max_retries.
    step = Step(description="Always fails", tool_hint="t", retry_count=2)
    result = StepResult(step_id=step.step_id, success=False, exception="too many times")
    plan = Plan(task="t", steps=[step])

    healing = healer.handle_failure(
        step=step, result=result, verdict=_exception_verdict(),
        executor=MagicMock(), planner=MagicMock(), plan=plan, registry=MagicMock(),
    )

    assert not healing.should_retry
    assert healing.abort
    assert step.status == StepStatus.FAILED


def test_retry_count_incremented():
    """retry_count on the step should increase after each handle_failure call."""
    config = _make_config(max_retries=3)
    healer = SelfHealingEngine(config)
    step = Step(description="Retry me", tool_hint="t", retry_count=0)
    result = StepResult(step_id=step.step_id, success=False, exception="oops")
    plan = Plan(task="t", steps=[step])

    healer.handle_failure(
        step=step, result=result, verdict=_exception_verdict(),
        executor=MagicMock(), planner=None, plan=plan, registry=MagicMock(),
    )
    assert step.retry_count == 1

    healer.handle_failure(
        step=step, result=result, verdict=_exception_verdict(),
        executor=MagicMock(), planner=None, plan=plan, registry=MagicMock(),
    )
    assert step.retry_count == 2
