"""Anvil CLI — Typer app.

Commands (exact behavior spec: App Flow §2):
  anvil init <agent_name>   — scaffolds a new agent dir from template
  anvil run <agent_name> "<task>" [--verbose] [--quiet]
  anvil trace <run_id>      — re-renders a past run's trace
  anvil trace --list        — lists past runs, most recent first

No other top-level commands in v1 (no `anvil deploy`/`anvil serve`).

Build in Phase 11, after Tracing (Phase 10) — see Implementation Plan.
"""

import typer

app = typer.Typer(help="Anvil — a local-first Python agent framework.")

# TODO (Phase 11): implement init, run, trace commands

if __name__ == "__main__":
    app()
