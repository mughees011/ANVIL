"""QualityEnforcer — orchestrates rule-based + optional LLM-graded checks.

check(step, result):
  1. Run all rule-based checks (checks.py) first — fast fail.
  2. Only if all pass AND step.rubric is set: run one extra Groq call
     grading StepResult against the rubric text (pass/fail + reason).
     Off by default — opt-in per-step, keeps cost/latency down.

Resolved design (was PRD open question #2): TRD §6.
Build in Phase 7 — see Implementation Plan.
"""

# TODO (Phase 7): implement QualityEnforcer.check()
