"""Anvil CLI — Typer app (Phase 11).

Commands (exact behavior spec: App Flow §2):
  anvil init <agent_name>   — scaffolds a new agent dir from template
  anvil run <agent_name> "<task>" [--verbose] [--quiet]
  anvil trace <run_id>      — re-renders a past run's trace
  anvil trace --list        — lists past runs, most recent first
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

app = typer.Typer(
    help="Anvil — a local-first Python agent framework.",
    no_args_is_help=True,
)
trace_app = typer.Typer(help="Inspect past run traces.")
app.add_typer(trace_app, name="trace")

_console = Console()
_RUNS_DIR = Path(".anvil/runs")

# ── Init command ───────────────────────────────────────────────────────────────

_AGENT_PY_TEMPLATE = '''\
"""Example agent using Anvil."""

from anvil.agent import AgentRunner
from anvil.config import load_config
from {name}.tools import MY_TOOLS  # Replace with your actual tools module


def main() -> None:
    config = load_config("{name}/anvil.config.yaml")
    runner = AgentRunner(config=config, tools=MY_TOOLS)
    result = runner.run("Your task here")
    print(f"Status: {{result.status}}")
    print(f"Trace: {{result.trace_path}}")


if __name__ == "__main__":
    main()
'''

_TOOLS_PY_TEMPLATE = '''\
"""Tools for the {name} agent."""

from pydantic import BaseModel
from anvil.tools.registry import tool, Tool


class ExampleParams(BaseModel):
    message: str


@tool(params_schema=ExampleParams)
def example_tool(message: str) -> str:
    """An example tool — replace with your real tools."""
    return f"Echo: {{message}}"


MY_TOOLS: list[Tool] = [example_tool]  # type: ignore
'''

_CONFIG_TEMPLATE = """\
name: {name}
planner_model: "llama-3.3-70b-versatile"
executor_model: "llama-3.3-70b-versatile"
max_retries: 3
memory_top_k: 5
halt_on_failure: true
allow_shell_tool: false
"""


@app.command()
def init(agent_name: str = typer.Argument(..., help="Name of the new agent.")) -> None:
    """Scaffold a new agent directory from a template."""
    agent_dir = Path(agent_name)
    if agent_dir.exists():
        _console.print(Text(f"Directory '{agent_name}' already exists. Aborting.", style="red bold"))
        raise typer.Exit(1)

    agent_dir.mkdir(parents=True)
    (agent_dir / "agent.py").write_text(
        _AGENT_PY_TEMPLATE.format(name=agent_name), encoding="utf-8"
    )
    (agent_dir / "tools.py").write_text(
        _TOOLS_PY_TEMPLATE.format(name=agent_name), encoding="utf-8"
    )
    (agent_dir / "anvil.config.yaml").write_text(
        _CONFIG_TEMPLATE.format(name=agent_name), encoding="utf-8"
    )
    (agent_dir / "__init__.py").write_text("", encoding="utf-8")

    _console.print(Text(f"✓ Created agent '{agent_name}' in ./{agent_name}/", style="green bold"))
    _console.print("\nNext steps:")
    _console.print(f"  1. Edit {agent_name}/tools.py — add your tools")
    _console.print(f"  2. Edit {agent_name}/anvil.config.yaml — set model/config")
    _console.print(f"  3. anvil run {agent_name} \"your task\"")


# ── Run command ────────────────────────────────────────────────────────────────

@app.command("run")
def run_agent(
    agent_name: str = typer.Argument(..., help="Agent directory name."),
    task: str = typer.Argument(..., help="Task to run."),
    verbose: bool = typer.Option(True, "--verbose/--quiet", help="Stream live trace output."),
) -> None:
    """Load and run an agent on a task."""
    from anvil.agent import AgentRunner
    from anvil.config import load_config, ConfigError

    config_path = Path(agent_name) / "anvil.config.yaml"
    if not config_path.exists():
        _console.print(
            Text(f"Config not found: {config_path}. Run `anvil init {agent_name}` first.", style="red bold")
        )
        raise typer.Exit(1)

    try:
        config = load_config(config_path)
    except ConfigError as exc:
        _console.print(Text(f"Configuration error: {exc}", style="red bold"))
        raise typer.Exit(1)

    # Dynamically import the agent's tools module if it exists.
    tools = []
    tools_path = Path(agent_name) / "tools.py"
    if tools_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"{agent_name}.tools", tools_path)
        module = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(module)  # type: ignore
        if hasattr(module, "MY_TOOLS"):
            tools = module.MY_TOOLS

    runner = AgentRunner(config=config, tools=tools, verbose=verbose)
    result = runner.run(task)

    if result.status == "failed":
        raise typer.Exit(1)


# ── Trace sub-commands ─────────────────────────────────────────────────────────

@trace_app.command("show")
def trace_show(
    run_id: str = typer.Argument(..., help="Run ID or prefix to display."),
) -> None:
    """Re-render a past run's trace to the terminal."""
    from anvil.tracing.trace import render_trace

    # Support prefix matching.
    matches = list(_RUNS_DIR.glob(f"{run_id}*.json")) if _RUNS_DIR.exists() else []
    if not matches:
        _console.print(Text(f"No trace found for run ID: {run_id}", style="red bold"))
        raise typer.Exit(1)
    render_trace(matches[0])


@trace_app.callback(invoke_without_command=True)
def trace_callback(
    ctx: typer.Context,
    list_runs: bool = typer.Option(False, "--list", help="List past runs."),
) -> None:
    """Inspect past run traces."""
    if list_runs or ctx.invoked_subcommand is None:
        _list_traces()


def _list_traces() -> None:
    """List past runs from .anvil/runs/, most recent first."""
    if not _RUNS_DIR.exists():
        _console.print(Text("No traces found. Run an agent first.", style="dim"))
        return

    files = sorted(_RUNS_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        _console.print(Text("No traces found.", style="dim"))
        return

    table = Table(title="Past Runs", show_header=True, header_style="cyan bold")
    table.add_column("Run ID", style="dim", no_wrap=True)
    table.add_column("Agent")
    table.add_column("Task")
    table.add_column("Status")
    table.add_column("Started At")

    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            status_style = "green" if data.get("final_status") == "success" else "red"
            table.add_row(
                data.get("run_id", f.stem)[:12],
                data.get("agent_name", "?"),
                data.get("task", "?")[:60],
                Text(data.get("final_status", "?"), style=status_style),
                data.get("started_at", "?")[:19],
            )
        except Exception:
            continue

    _console.print(table)


if __name__ == "__main__":
    app()
