"""Rule-based quality checks — zero extra LLM cost, always run first.

Built-ins: no_tool_error, output_not_empty,
output_matches_schema(pydantic_model), file_exists(path).

Agent authors can register custom rule functions:
Callable[[StepResult], bool].

Spec: TRD §6. Build in Phase 7 — see Implementation Plan.
"""

# TODO (Phase 7): implement built-in rule checks + custom rule registration
