"""AgentRunner — top-level orchestration entrypoint (Phase 9).

Wires Planner + Executor + QualityEnforcer + SelfHealingEngine + Memory
+ Tracer together. Implements the exact control flow from TRD §3 and
App Flow §3.

Usage::

    runner = AgentRunner(config=cfg, tools=[my_tool])
    result = runner.run("Do something useful")
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from anvil.config import AgentConfig
from anvil.execution.executor import Executor
from anvil.healing.self_heal import SelfHealingEngine
from anvil.llm.groq_client import GroqClient
from anvil.memory.store import MemoryStore
from anvil.planning.models import AgentResult, Plan, StepStatus
from anvil.planning.planner import Planner
from anvil.quality.enforcer import QualityEnforcer
from anvil.tools.registry import Tool, ToolRegistry
from anvil.tracing.trace import RunTrace


class AgentRunner:
    """Top-level agent orchestrator.

    Args:
        config: Loaded AgentConfig (includes groq_api_key).
        tools: List of Tool objects to register.
        verbose: Stream live trace output to terminal (default True).
        chroma_path: Override ChromaDB storage directory.
    """

    def __init__(
        self,
        config: AgentConfig,
        tools: Optional[list[Tool]] = None,
        verbose: bool = True,
        chroma_path: str | Path = ".anvil/chroma/",
    ) -> None:
        self.config = config
        self._verbose = verbose

        # Wire up all subsystems.
        self._groq = GroqClient(api_key=config.groq_api_key)
        self._registry = ToolRegistry()
        for t in (tools or []):
            self._registry.register(t)

        self._memory = MemoryStore(
            agent_name=config.name,
            chroma_path=chroma_path,
        )
        self._planner = Planner(
            groq_client=self._groq,
            model=config.planner_model,
        )
        self._executor = Executor(
            groq_client=self._groq,
            registry=self._registry,
            config=config,
            model=config.executor_model,
        )
        self._quality = QualityEnforcer(groq_client=self._groq, model=config.executor_model)
        self._healer = SelfHealingEngine(config=config)

    def run(self, task: str) -> AgentResult:
        """Execute the agent on the given task.

        Implements the exact sequence from App Flow §3 steps [1]–[6]:
          [1] Recall relevant memory.
          [2] Generate a Plan.
          [3] For each Step: execute → quality check → heal on failure.
          [4] All steps done (or aborted).
          [5] Write trace to disk.
          [6] Clear episodic memory.

        Args:
            task: Natural-language task description.

        Returns:
            AgentResult with status, summary, and trace path.
        """
        trace = RunTrace(
            agent_name=self.config.name,
            task=task,
            verbose=self._verbose,
        )

        if self._verbose:
            from rich.console import Console
            from rich.text import Text
            Console().print(Text(f'\n→ Task received: "{task}"', style="cyan bold"))

        # ── [1] Recall relevant memory ─────────────────────────────────────────
        memory_hits = self._memory.recall(
            query=task,
            k=self.config.memory_top_k,
            collection="semantic",
        )
        if memory_hits and self._verbose:
            from rich.console import Console
            from rich.text import Text
            Console().print(
                Text(f"◆ Recalling relevant memory... ({len(memory_hits)} hits)", style="magenta")
            )

        # ── [2] Generate a Plan ────────────────────────────────────────────────
        plan = self._planner.generate_plan(
            task=task,
            registry=self._registry,
            memory_hits=memory_hits or None,
        )
        trace.record_plan(plan)

        final_status = "success"
        abort_reason = ""

        # ── [3] Execute steps ──────────────────────────────────────────────────
        for step_index, step in enumerate(plan.steps, 1):
            trace.record_step_start(step_index, step.description)
            failure_context: Optional[str] = None

            while True:
                # [3a] Execute the step.
                if trace.verbose and step.tool_hint:
                    trace.record_tool_call(step.tool_hint)
                result = self._executor.run_step(step, prior_context=failure_context)

                # [3b-3c] Quality check.
                verdict = self._quality.check(step, result)
                result.quality_check = verdict.to_model()
                result.retries = step.retry_count

                if verdict.passed:
                    # [3d] Success path — record result and remember.
                    step.status = StepStatus.SUCCESS
                    trace.record_step_result(result)
                    summary_text = f"{step.description} → {result.summary or 'completed'}"
                    self._memory.remember(
                        summary_text,
                        collection="episodic",
                        run_id=trace.run_id,
                        step_id=step.step_id,
                    )
                    trace.record_memory_write("episodic")
                    break  # Next step.
                else:
                    # [3d] Failure path — invoke self-heal.
                    healing = self._healer.handle_failure(
                        step=step,
                        result=result,
                        verdict=verdict,
                        executor=self._executor,
                        planner=self._planner,
                        plan=plan,
                        registry=self._registry,
                    )

                    if healing.abort:
                        # Max retries exceeded.
                        trace.record_step_result(result)
                        final_status = "failed"
                        abort_reason = healing.failure_reason
                        break

                    # Retry — update step and context for next loop iteration.
                    if healing.updated_step:
                        step = healing.updated_step
                    failure_context = healing.failure_reason
                    trace.record_retry(
                        step_index=step_index,
                        attempt=step.retry_count,
                        max_retries=self.config.max_retries,
                        reason=failure_context,
                    )

            if final_status == "failed" and self.config.halt_on_failure:
                break  # Stop processing further steps.

        # ── [5] Finalize trace ─────────────────────────────────────────────────
        trace_path = trace.finalize(final_status)

        # ── [6] Clear episodic memory ──────────────────────────────────────────
        self._memory.clear_episodic()

        return AgentResult(
            status=final_status,
            output_summary=abort_reason if final_status == "failed" else (
                plan.steps[-1].description if plan.steps else task
            ),
            trace_path=str(trace_path),
            run_id=trace.run_id,
        )
