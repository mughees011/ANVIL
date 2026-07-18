"""Plan, Step, StepResult — core data models.

Pydantic models, JSON-serializable (needed by both Planner output
and Tracer). Step fields: id, description, tool_hint, depends_on,
status, retry_count, rubric (optional, for LLM-graded quality checks).

Exact JSON shape these must round-trip to: Backend Schema §4.
Build this in Phase 4, BEFORE Planner/Executor — see Implementation
Plan's "Explicit Ordering Rationale" for why order matters here.
"""

# TODO (Phase 4): implement Plan, Step, StepResult, status enums
