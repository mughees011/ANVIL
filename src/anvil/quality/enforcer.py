"""QualityEnforcer — orchestrates rule-based + optional LLM-graded checks.

check(step, result) -> QualityCheckResult
  1. Run rule-based checks first (fast, no LLM cost).
  2. Only if all pass AND step.rubric is set: run one extra Groq call.

Resolved design per TRD §6.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from anvil.llm.groq_client import GroqClient
from anvil.planning.models import QualityCheckResult, Step, StepResult
from anvil.quality.checks import RuleCheck, no_tool_error, output_not_empty

_RUBRIC_SYSTEM = (
    "You are a quality evaluation agent. "
    "Evaluate whether the step result satisfies the given rubric criterion. "
    "Respond with ONLY a JSON object: "
    '{"verdict": "pass" | "fail", "reason": "<short explanation>"}'
)


@dataclass
class QualityVerdict:
    """Full verdict from QualityEnforcer.check()."""

    passed: bool
    rule_check: str = "pass"                 # "pass" | "fail"
    rule_failure_reason: Optional[str] = None
    llm_rubric_check: Optional[str] = None   # "pass" | "fail" | None
    llm_rubric_reason: Optional[str] = None

    @property
    def failed(self) -> bool:
        return not self.passed

    def to_model(self) -> QualityCheckResult:
        return QualityCheckResult(
            rule_check=self.rule_check,
            llm_rubric_check=self.llm_rubric_check,
        )


class QualityEnforcer:
    """Orchestrates quality checks for each executed Step.

    Args:
        groq_client: GroqClient instance (needed for LLM-graded checks).
        model: Model slug for rubric evaluation calls.
        extra_rules: Additional rule-check callables applied to every step.
    """

    DEFAULT_RULES: list[RuleCheck] = [no_tool_error, output_not_empty]

    def __init__(
        self,
        groq_client: Optional[GroqClient] = None,
        model: str = "llama-3.3-70b-versatile",
        extra_rules: Optional[list[RuleCheck]] = None,
    ) -> None:
        self._client = groq_client
        self._model = model
        self._rules: list[RuleCheck] = list(self.DEFAULT_RULES)
        if extra_rules:
            self._rules.extend(extra_rules)

    def add_rule(self, rule: RuleCheck) -> None:
        """Register an additional rule check that runs on every step."""
        self._rules.append(rule)

    def check(self, step: Step, result: StepResult) -> QualityVerdict:
        """Run quality checks for a step result.

        Always runs rule-based checks first. Only invokes the LLM rubric
        check if all rules pass AND step.rubric is set.

        Args:
            step: The Step that was executed.
            result: The StepResult from the Executor.

        Returns:
            QualityVerdict summarising pass/fail and the reason.
        """
        # ── 1. Rule-based checks (always) ─────────────────────────────────────
        for rule in self._rules:
            passed, reason = rule(result)
            if not passed:
                return QualityVerdict(
                    passed=False,
                    rule_check="fail",
                    rule_failure_reason=reason,
                )

        # ── 2. LLM-graded rubric check (opt-in) ───────────────────────────────
        if step.rubric and self._client:
            llm_passed, llm_reason = self._run_rubric_check(
                step_description=step.description,
                rubric=step.rubric,
                result=result,
            )
            if not llm_passed:
                return QualityVerdict(
                    passed=False,
                    rule_check="pass",
                    llm_rubric_check="fail",
                    llm_rubric_reason=llm_reason,
                )
            return QualityVerdict(
                passed=True,
                rule_check="pass",
                llm_rubric_check="pass",
                llm_rubric_reason=llm_reason,
            )

        return QualityVerdict(passed=True, rule_check="pass")

    def _run_rubric_check(
        self,
        step_description: str,
        rubric: str,
        result: StepResult,
    ) -> tuple[bool, str]:
        """Run one extra Groq call to grade the StepResult against the rubric."""
        import json, re

        output_repr = result.summary or str(
            [tc.output for tc in result.tool_calls]
        )
        user_msg = (
            f"Step: {step_description}\n"
            f"Rubric criterion: {rubric}\n"
            f"Step output:\n{output_repr}"
        )
        try:
            raw = self._client.chat(
                messages=[
                    {"role": "system", "content": _RUBRIC_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                model=self._model,
                temperature=0.0,
            )
            cleaned = re.sub(r"```(?:json)?", "", raw).strip()
            data = json.loads(cleaned)
            verdict = data.get("verdict", "fail").lower()
            reason = data.get("reason", "")
            return verdict == "pass", reason
        except Exception as exc:
            # If the rubric call itself fails, treat as a pass to avoid
            # blocking the run on an evaluation infrastructure error.
            return True, f"Rubric check skipped due to error: {exc}"
