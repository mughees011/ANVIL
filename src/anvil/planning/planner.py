"""Planner — generates a Plan from a Task + available Tools + Memory.

generate_plan(task, tools, memory) -> Plan

Prompts the LLM via GroqClient.chat() (temperature=0.2, deterministic-
leaning), parses response into Plan/Step objects. MUST fail loudly on
malformed LLM output — never pass bad data downstream silently.

Also used for partial re-planning during self-heal (only the failed
step + its downstream dependents, not a full regeneration) — see
App Flow §3 for the exact branching logic.

Build this in Phase 5 — see Implementation Plan.
"""

# TODO (Phase 5): implement Planner.generate_plan()
