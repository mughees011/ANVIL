"""Plan, Step, StepResult — core data models (Phase 4).

Pydantic models, JSON-serializable. Exact JSON shape per Backend Schema §4.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class StepStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRIED = "retried"


class QualityVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"


class ToolCall(BaseModel):
    """Record of a single tool call made during step execution."""

    tool: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: Any = None
    error: Optional[str] = None


class QualityCheckResult(BaseModel):
    """Result of the quality check for a step."""

    rule_check: str = "pass"         # "pass" | "fail"
    llm_rubric_check: Optional[str] = None  # "pass" | "fail" | None


class Step(BaseModel):
    """One unit of work in a Plan."""

    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    tool_hint: str = ""               # Suggested tool name; may be empty
    depends_on: list[str] = Field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    retry_count: int = 0
    rubric: Optional[str] = None      # If set, LLM-graded quality check runs


class Plan(BaseModel):
    """Ordered list of Steps for a given Task."""

    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task: str
    steps: list[Step] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class StepResult(BaseModel):
    """Captured output from executing a Step."""

    step_id: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    summary: str = ""                  # Human-readable summary of the result
    success: bool = True
    exception: Optional[str] = None    # Stringified exception if one was raised
    duration_seconds: float = 0.0
    quality_check: QualityCheckResult = Field(default_factory=QualityCheckResult)
    retries: int = 0


class AgentResult(BaseModel):
    """Final result returned by AgentRunner.run()."""

    status: str                        # "success" | "failed"
    output_summary: str = ""
    trace_path: Optional[str] = None
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
