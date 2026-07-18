"""Planner — generates a Plan from a Task + available Tools + Memory.

generate_plan(task, tools, memory) -> Plan

Prompts the LLM via GroqClient.chat() (temperature=0.2),
parses response into Plan/Step objects. Fails loudly on malformed
LLM output — never passes bad data downstream silently.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Optional

from anvil.llm.groq_client import GroqClient
from anvil.memory.store import MemoryHit
from anvil.planning.models import Plan, Step
from anvil.tools.registry import ToolRegistry

if TYPE_CHECKING:
    pass

_SYSTEM_PROMPT = """\
You are an expert planning agent. Given a task, a list of available tools, \
and relevant memory context, produce a structured execution plan.

Respond ONLY with a valid JSON object matching this schema:
{
  "steps": [
    {
      "description": "<what this step does>",
      "tool_hint": "<name of the primary tool to use, or empty string>",
      "depends_on": ["<step_id of prerequisite step, if any>"],
      "rubric": "<optional: a short criterion for LLM-graded quality check, or null>"
    }
  ]
}

Rules:
- Use only tools from the provided tool list.
- tool_hint must exactly match a tool name from the list, or be an empty string.
- depends_on must reference step indices (0-based) or empty array.
- Be concise. 3–7 steps is typical. Avoid redundant steps.
- Output ONLY the JSON object, no markdown fences, no explanation.
"""


class PlannerError(Exception):
    """Raised when the LLM returns a plan that cannot be parsed."""


class Planner:
    """Generates structured Plans from natural-language tasks.

    Args:
        groq_client: Initialized GroqClient.
        model: Groq model slug to use for planning.
        temperature: Sampling temperature (default 0.2 for determinism).
    """

    def __init__(
        self,
        groq_client: GroqClient,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.2,
    ) -> None:
        self._client = groq_client
        self._model = model
        self._temperature = temperature

    def generate_plan(
        self,
        task: str,
        registry: ToolRegistry,
        memory_hits: Optional[list[MemoryHit]] = None,
    ) -> Plan:
        """Generate a Plan for the given task.

        Args:
            task: The user-provided task description.
            registry: Registered tools the agent can use.
            memory_hits: Optional recalled memory snippets to inject as context.

        Returns:
            A validated Plan object.

        Raises:
            PlannerError: If the LLM response cannot be parsed into a valid Plan.
        """
        tool_list = "\n".join(
            f"- {t.name}: {t.description}" for t in registry.all()
        ) or "(no tools registered)"

        memory_block = ""
        if memory_hits:
            snippets = "\n".join(f"  • {h.document}" for h in memory_hits)
            memory_block = f"\n\nRelevant memory context:\n{snippets}"

        user_message = (
            f"Task: {task}\n\n"
            f"Available tools:\n{tool_list}"
            f"{memory_block}"
        )

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        raw = self._client.chat(
            messages=messages,
            model=self._model,
            temperature=self._temperature,
        )

        return self._parse_plan(task=task, raw=raw, registry=registry)

    def _parse_plan(self, task: str, raw: str, registry: ToolRegistry) -> Plan:
        """Parse the LLM's JSON response into a Plan. Fails loudly on bad output."""
        # Strip markdown fences if the model included them despite instructions.
        cleaned = re.sub(r"```(?:json)?", "", raw).strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise PlannerError(
                f"Planner returned non-JSON output. "
                f"Raw response: {raw!r}"
            ) from exc

        if "steps" not in data or not isinstance(data["steps"], list):
            raise PlannerError(
                f"Planner response missing 'steps' key or steps is not a list. "
                f"Got: {data}"
            )

        valid_tools = set(registry.names())
        steps: list[Step] = []
        for i, raw_step in enumerate(data["steps"]):
            if not isinstance(raw_step, dict):
                raise PlannerError(f"Step {i} is not a dict: {raw_step}")
            if "description" not in raw_step:
                raise PlannerError(f"Step {i} missing 'description' field: {raw_step}")

            tool_hint = raw_step.get("tool_hint", "") or ""
            # If the planner hallucinated a tool name, keep it but warn —
            # the Executor will treat it as a rule_check failure.
            rubric = raw_step.get("rubric") or None
            depends_on = raw_step.get("depends_on") or []

            step = Step(
                description=raw_step["description"],
                tool_hint=tool_hint,
                depends_on=depends_on,
                rubric=rubric,
            )
            steps.append(step)

        if not steps:
            raise PlannerError("Planner returned an empty steps list.")

        return Plan(task=task, steps=steps)
