"""RunTrace — structured trace of a run, JSON writer + Rich live printer.

Canonical JSON schema (single source of truth): Backend Schema §4.
Written to .anvil/runs/{run_id}.json on completion.

Live verbose output uses the color/symbol vocabulary from
UI/UX Design Brief §2-3 exactly — do not invent ad hoc colors here.
Never write GROQ_API_KEY or any secret into the trace, even if it
somehow ends up in a tool output — explicitly filter it out.

Build in Phase 10 — see Implementation Plan.
"""

# TODO (Phase 10): implement RunTrace, JSON writer, Rich live printer
