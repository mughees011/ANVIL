"""SelfHealingEngine — retry/repair loop on QualityCheck failure (Phase 8).

handle_failure(step, result, verdict, executor, planner, plan, config)
  - Tool execution exception -> same-step retry.
  - Quality/rubric failure    -> partial re-plan.
  - Exceeds max_retries      -> marks step FAILED, signals abort.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from anvil.planning.models import Plan, Step, StepResult, StepStatus
from anvil.quality.enforcer import QualityVerdict

if TYPE_CHECKING:
    from anvil.config import AgentConfig
    from anvil.execution.executor import Executor
    from anvil.planning.planner import Planner
    from anvil.tools.registry import ToolRegistry


class HealingResult:
    """What the SelfHealingEngine decided to do."""

    def __init__(
        self,
        should_retry: bool,
        updated_step: Optional[Step] = None,
        updated_plan: Optional[Plan] = None,
        abort: bool = False,
        failure_reason: str = "",
    ) -> None:
        self.should_retry = should_retry
        self.updated_step = updated_step
        self.updated_plan = updated_plan
        self.abort = abort
        self.failure_reason = failure_reason


class SelfHealingEngine:
    """Handles step failures by retrying or triggering a partial re-plan.

    Args:
        config: AgentConfig (provides max_retries, halt_on_failure).
    """

    def __init__(self, config: "AgentConfig") -> None:
        self._config = config

    def handle_failure(
        self,
        step: Step,
        result: StepResult,
        verdict: QualityVerdict,
        executor: "Executor",
        planner: Optional["Planner"],
        plan: Plan,
        registry: "ToolRegistry",
    ) -> HealingResult:
        """Decide what to do after a step fails quality checks.

        Decision tree (App Flow §3):
          - Step exception (result.exception set) -> same-step retry.
          - Quality/rubric failure -> partial re-plan if planner is available,
            else same-step retry with failure context.
          - Retry count exceeds max_retries -> mark FAILED, abort if configured.

        Args:
            step: The failed Step (with retry_count already incremented by caller).
            result: StepResult from the Executor.
            verdict: QualityVerdict that triggered this call.
            executor: Executor instance (used for same-step retry).
            planner: Planner instance (used for partial re-plan). May be None.
            plan: The current Plan (for re-planning downstream steps).
            registry: Tool registry.

        Returns:
            HealingResult with the decided action.
        """
        if step.retry_count >= self._config.max_retries:
            step.status = StepStatus.FAILED
            return HealingResult(
                should_retry=False,
                abort=True,
                failure_reason=(
                    f"Step '{step.description}' failed after "
                    f"{self._config.max_retries} retries. "
                    f"Last failure: {verdict.rule_failure_reason or verdict.llm_rubric_reason}"
                ),
            )

        step.retry_count += 1
        step.status = StepStatus.RETRIED

        # ── Branch A: tool execution exception → same-step retry ──────────────
        if result.exception:
            failure_context = (
                f"Previous attempt raised: {result.exception}"
            )
            return HealingResult(
                should_retry=True,
                updated_step=step,
                failure_reason=failure_context,
            )

        # ── Branch B: quality/rubric failure → partial re-plan ────────────────
        if planner is not None:
            failure_context = (
                f"Step '{step.description}' completed but failed quality check: "
                f"{verdict.llm_rubric_reason or verdict.rule_failure_reason}"
            )
            # Re-plan just the failed step + its downstream dependents.
            updated_plan = self._partial_replan(
                failed_step=step,
                plan=plan,
                planner=planner,
                registry=registry,
                failure_context=failure_context,
            )
            return HealingResult(
                should_retry=True,
                updated_step=updated_plan.steps[0] if updated_plan.steps else step,
                updated_plan=updated_plan,
                failure_reason=failure_context,
            )

        # ── Fallback: no planner → same-step retry with context ───────────────
        failure_context = (
            f"Quality check failed: "
            f"{verdict.llm_rubric_reason or verdict.rule_failure_reason}"
        )
        return HealingResult(
            should_retry=True,
            updated_step=step,
            failure_reason=failure_context,
        )

    def _partial_replan(
        self,
        failed_step: Step,
        plan: Plan,
        planner: "Planner",
        registry: "ToolRegistry",
        failure_context: str,
    ) -> Plan:
        """Re-generate a plan fragment for the failed step + its dependents."""
        # Build a task description that includes the failure context.
        partial_task = (
            f"Re-plan this step (it previously failed):\n"
            f"Step: {failed_step.description}\n"
            f"Failure context: {failure_context}\n"
            f"Provide a revised approach."
        )
        try:
            new_plan = planner.generate_plan(
                task=partial_task,
                registry=registry,
                memory_hits=None,
            )
            return new_plan
        except Exception:
            # If re-planning itself fails, return a plan with just the
            # original step so the caller retries it with context.
            return Plan(task=partial_task, steps=[failed_step])
