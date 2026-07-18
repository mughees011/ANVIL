"""RunTrace — structured trace of a run, JSON writer + Rich live printer.

Canonical JSON schema (single source of truth): Backend Schema §4.
Written to .anvil/runs/{run_id}.json on completion.

Live verbose output uses the color/symbol vocabulary from
UI/UX Design Brief §2-3 exactly.
Never writes GROQ_API_KEY or any secret into the trace.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.text import Text

from anvil.planning.models import Plan, StepResult, StepStatus

_RUNS_DIR = Path(".anvil/runs")
_console = Console()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunTrace:
    """Accumulates trace data for a single run and writes it to disk.

    Args:
        run_id: Unique run identifier.
        agent_name: Name of the running agent.
        task: The task string given to the agent.
        verbose: If True, print live Rich output as steps execute.
    """

    def __init__(
        self,
        agent_name: str,
        task: str,
        run_id: Optional[str] = None,
        verbose: bool = True,
    ) -> None:
        self.run_id = run_id or str(uuid.uuid4())
        self.agent_name = agent_name
        self.task = task
        self.verbose = verbose
        self.started_at = _now_iso()
        self.ended_at: Optional[str] = None
        self.final_status = "pending"
        self._plan: Optional[Plan] = None
        self._step_results: list[StepResult] = []

    # ── Recording API ──────────────────────────────────────────────────────────

    def record_plan(self, plan: Plan) -> None:
        self._plan = plan
        if self.verbose:
            _console.print(
                Text(f"\n→ Plan generated ({len(plan.steps)} steps)", style="cyan bold")
            )
            for i, step in enumerate(plan.steps, 1):
                _console.print(f"  {i}. {step.description}", style="white")

    def record_step_start(self, step_index: int, step_description: str) -> None:
        if self.verbose:
            _console.print(
                Text(f"\n→ Step {step_index}: {step_description}", style="cyan")
            )

    def record_tool_call(self, tool_name: str) -> None:
        if self.verbose:
            _console.print(f"  … calling tool: {tool_name}", style="dim white")

    def record_step_result(self, result: StepResult) -> None:
        self._step_results.append(result)
        if self.verbose:
            if result.success:
                _console.print(
                    Text(f"  ✓ Step complete", style="green bold")
                )
            else:
                _console.print(
                    Text(f"  ✗ Step failed: {result.exception}", style="red bold")
                )

    def record_retry(self, step_index: int, attempt: int, max_retries: int, reason: str) -> None:
        if self.verbose:
            _console.print(
                Text(
                    f"  ↻ Step {step_index} failed quality check — "
                    f"retrying (attempt {attempt}/{max_retries}): {reason}",
                    style="yellow bold",
                )
            )

    def record_memory_write(self, collection: str) -> None:
        if self.verbose:
            _console.print(
                Text(f"  ◆ memory.remember() → {collection}", style="magenta")
            )

    def finalize(self, final_status: str) -> Path:
        """Mark the run as complete and write the trace JSON to disk.

        Args:
            final_status: "success" or "failed".

        Returns:
            Path to the written trace file.
        """
        self.ended_at = _now_iso()
        self.final_status = final_status

        if self.verbose:
            style = "green bold" if final_status == "success" else "red bold"
            _console.print(
                Text(
                    f"\n＝ Task {final_status}. Trace saved to "
                    f".anvil/runs/{self.run_id[:8]}.json",
                    style=style,
                )
            )

        return self._write()

    # ── Serialisation ──────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return the trace as a plain dict matching Backend Schema §4."""
        plan_steps = []
        if self._plan:
            for step in self._plan.steps:
                plan_steps.append({
                    "step_id": step.step_id,
                    "description": step.description,
                    "status": step.status.value if hasattr(step.status, "value") else step.status,
                })

        steps_data = []
        for r in self._step_results:
            steps_data.append({
                "step_id": r.step_id,
                "tool_calls": [
                    {
                        "tool": tc.tool,
                        "input": tc.input,
                        "output": tc.output,
                    }
                    for tc in r.tool_calls
                ],
                "quality_check": {
                    "rule_check": r.quality_check.rule_check,
                    "llm_rubric_check": r.quality_check.llm_rubric_check,
                },
                "retries": r.retries,
            })

        return {
            "run_id": self.run_id,
            "agent_name": self.agent_name,
            "task": self.task,
            "plan": plan_steps,
            "steps": steps_data,
            "final_status": self.final_status,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
        }

    def _write(self) -> Path:
        """Write the trace JSON to .anvil/runs/{run_id}.json."""
        _RUNS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = _RUNS_DIR / f"{self.run_id}.json"
        data = self.to_dict()
        out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return out_path


def render_trace(trace_path: str | Path) -> None:
    """Re-render a past run's trace from a JSON file to the terminal (anvil trace <id>)."""
    path = Path(trace_path)
    if not path.exists():
        _console.print(Text(f"Trace file not found: {path}", style="red bold"))
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    _console.print(Text(f"\n→ Task: {data['task']}", style="cyan bold"))
    _console.print(Text(f"  Agent: {data['agent_name']} | Run ID: {data['run_id']}", style="dim"))
    _console.print(Text(f"\n→ Plan ({len(data['plan'])} steps)", style="cyan"))
    for i, step in enumerate(data["plan"], 1):
        status = step.get("status", "?")
        color = "green" if status == "success" else ("yellow" if status == "retried" else "red")
        _console.print(f"  {i}. [{status}] {step['description']}", style=color)

    _console.print(Text(f"\n＝ Final status: {data['final_status']}", style="bold"))
