"""Executor — runs one Step at a time (Phase 6).

run_step(step, registry, groq_client, config) -> StepResult
"""

from __future__ import annotations

import json
import time
from typing import Any, Optional

from anvil.config import AgentConfig
from anvil.llm.groq_client import GroqClient
from anvil.planning.models import Step, StepResult, ToolCall
from anvil.tools.builtin_shell import _execute_shell_command, run_shell_command
from anvil.tools.registry import ToolRegistry

_EXECUTOR_SYSTEM = (
    "You are a precise execution agent. "
    "Given a step description and available tools, call the most appropriate tool "
    "with the correct arguments. Call exactly one tool per response unless the step "
    "explicitly requires multiple sequential calls."
)


class Executor:
    """Runs individual Steps against the tool registry.

    Args:
        groq_client: Initialized GroqClient.
        registry: Registered tools.
        config: AgentConfig (needed for shell tool sandboxing).
        model: Groq model slug for tool-call decisions.
    """

    def __init__(
        self,
        groq_client: GroqClient,
        registry: ToolRegistry,
        config: AgentConfig,
        model: str = "llama-3.3-70b-versatile",
    ) -> None:
        self._client = groq_client
        self._registry = registry
        self._config = config
        self._model = model

    def run_step(
        self,
        step: Step,
        prior_context: Optional[str] = None,
    ) -> StepResult:
        """Execute a single Step and return its StepResult.

        Args:
            step: The Step to execute.
            prior_context: Optional failure context from a previous attempt
                           (injected by SelfHealingEngine on retries).

        Returns:
            StepResult capturing tool calls, output, and success/failure.
        """
        start = time.monotonic()
        tool_calls: list[ToolCall] = []

        user_content = f"Step: {step.description}"
        if prior_context:
            user_content += f"\n\nPrevious attempt failed:\n{prior_context}"

        messages = [
            {"role": "system", "content": _EXECUTOR_SYSTEM},
            {"role": "user", "content": user_content},
        ]

        # If a tool_hint is given, verify it exists early.
        if step.tool_hint and not self._registry.get(step.tool_hint):
            # Hallucinated tool name — return a failure result so SelfHealingEngine
            # can trigger a partial re-plan (App Flow §4).
            return StepResult(
                step_id=step.step_id,
                success=False,
                exception=f"Tool '{step.tool_hint}' not found in registry. "
                          f"Available tools: {self._registry.names()}",
                duration_seconds=time.monotonic() - start,
            )

        try:
            groq_tools = self._registry.to_groq_schema()
            message = self._client.chat_with_tools(
                messages=messages,
                tools=groq_tools,
                model=self._model,
                temperature=0.0,
            )

            # No tool call made — treat as a plain text response.
            if not hasattr(message, "tool_calls") or not message.tool_calls:
                content = getattr(message, "content", "") or ""
                return StepResult(
                    step_id=step.step_id,
                    tool_calls=[],
                    summary=content,
                    success=True,
                    duration_seconds=time.monotonic() - start,
                )

            # Execute each tool call returned by the model.
            for tc in message.tool_calls:
                fn_name = tc.function.name
                fn_args_raw = tc.function.arguments or "{}"

                try:
                    fn_args = json.loads(fn_args_raw)
                except json.JSONDecodeError:
                    fn_args = {}

                tool_obj = self._registry.get(fn_name)
                if tool_obj is None:
                    tool_calls.append(ToolCall(
                        tool=fn_name,
                        input=fn_args,
                        error=f"Tool '{fn_name}' not found in registry.",
                    ))
                    return StepResult(
                        step_id=step.step_id,
                        tool_calls=tool_calls,
                        success=False,
                        exception=f"Tool '{fn_name}' not found in registry.",
                        duration_seconds=time.monotonic() - start,
                    )

                # Special handling for sandboxed shell tool.
                if fn_name == "run_shell_command":
                    output = self._run_shell_safe(fn_args)
                else:
                    output = tool_obj.execute(**fn_args)

                tool_calls.append(ToolCall(tool=fn_name, input=fn_args, output=output))

            summary = tool_calls[-1].output if tool_calls else ""
            return StepResult(
                step_id=step.step_id,
                tool_calls=tool_calls,
                summary=str(summary),
                success=True,
                duration_seconds=time.monotonic() - start,
            )

        except Exception as exc:
            return StepResult(
                step_id=step.step_id,
                tool_calls=tool_calls,
                success=False,
                exception=str(exc),
                duration_seconds=time.monotonic() - start,
            )

    def _run_shell_safe(self, args: dict) -> dict:
        """Run run_shell_command after verifying shell config is present."""
        if not self._config.allow_shell_tool:
            raise PermissionError(
                "run_shell_command is disabled. Set allow_shell_tool=true in anvil.config.yaml."
            )
        if not self._config.shell_jail_dir:
            raise PermissionError(
                "shell_jail_dir must be set when allow_shell_tool=true."
            )
        return _execute_shell_command(
            cmd=args.get("cmd", []),
            jail_dir=self._config.shell_jail_dir,
            timeout=args.get("timeout") or self._config.shell_timeout_seconds,
        )
