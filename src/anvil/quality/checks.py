"""Rule-based quality checks — zero extra LLM cost, always run first.

Built-ins: no_tool_error, output_not_empty, output_matches_schema, file_exists.
Agent authors can register custom rule functions: Callable[[StepResult], bool].
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional, Type

from pydantic import BaseModel

from anvil.planning.models import StepResult


# ── Type alias ─────────────────────────────────────────────────────────────────

RuleCheck = Callable[[StepResult], tuple[bool, str]]
"""A rule check is a callable that takes a StepResult and returns (passed, reason)."""


# ── Built-in rule functions ────────────────────────────────────────────────────

def no_tool_error(result: StepResult) -> tuple[bool, str]:
    """Fails if the step raised an exception during execution."""
    if result.exception:
        return False, f"Tool raised an exception: {result.exception}"
    return True, "No exception"


def output_not_empty(result: StepResult) -> tuple[bool, str]:
    """Fails if the step produced no meaningful output."""
    if not result.summary and not result.tool_calls:
        return False, "Step produced no output"
    if result.tool_calls:
        last = result.tool_calls[-1]
        if last.output is None and last.error:
            return False, f"Last tool call errored: {last.error}"
    return True, "Output is non-empty"


def output_matches_schema(schema: Type[BaseModel]) -> RuleCheck:
    """Factory: returns a rule that validates the last tool output against a Pydantic model."""
    def _check(result: StepResult) -> tuple[bool, str]:
        if not result.tool_calls:
            return False, "No tool calls to validate"
        output = result.tool_calls[-1].output
        if not isinstance(output, dict):
            return False, f"Output is not a dict, cannot validate against {schema.__name__}"
        try:
            schema(**output)
            return True, f"Output matches {schema.__name__}"
        except Exception as exc:
            return False, f"Output does not match {schema.__name__}: {exc}"
    _check.__name__ = f"output_matches_{schema.__name__}"
    return _check


def file_exists(path: str) -> RuleCheck:
    """Factory: returns a rule that checks whether a file path exists after the step."""
    def _check(result: StepResult) -> tuple[bool, str]:
        if Path(path).exists():
            return True, f"File exists: {path}"
        return False, f"Expected file not found: {path}"
    _check.__name__ = f"file_exists_{path}"
    return _check
