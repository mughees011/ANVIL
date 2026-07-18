"""Executor — runs one Step at a time.

run_step(step) -> StepResult

Resolves step.tool_hint against ToolRegistry, calls
GroqClient.chat_with_tools() (temperature=0 where possible) to get
the actual tool call + args, executes the tool function, captures
output/exception/duration into StepResult.

If tool_hint doesn't resolve to a real tool: treat as a rule_check
failure (not a crash) — usually means the Planner hallucinated a tool
name; triggers SelfHealingEngine partial re-plan. See App Flow §4.

Build this in Phase 6 — see Implementation Plan.
"""

# TODO (Phase 6): implement Executor.run_step()
