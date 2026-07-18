"""SelfHealingEngine — retry/repair loop on QualityCheck failure.

handle_failure(step, result, verdict):
  - Tool execution exception -> same-step retry (re-invoke
    Executor.run_step with failure context appended).
  - Quality/rubric failure (ran fine, but wrong) -> partial re-plan
    (re-invoke Planner.generate_plan for just the failed step +
    downstream dependents, NOT the whole Plan).
  - Tracks retry_count against AgentConfig.max_retries (default 3).
  - Exceeds max_retries -> step.status = FAILED; if
    config.halt_on_failure (default True), whole run halts, partial
    trace still written.

Only triggered by logic failures — transport errors (429/5xx) are
handled separately in GroqClient, not here. See TRD §7, App Flow §3-4.

Build in Phase 8 — see Implementation Plan.
"""

# TODO (Phase 8): implement SelfHealingEngine.handle_failure()
