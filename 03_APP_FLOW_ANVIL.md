# App Flow — Anvil
### User Journeys & Execution Logic

**Doc status:** Draft v1
**Note on scope:** Anvil is a CLI + importable Python library, not a GUI app. "App Flow" here covers two things: (1) the human's journey as a developer installing/using Anvil, and (2) the internal decision flow the framework runs through for every task. Both are specified so nothing is ambiguous at implementation time.

---

## 1. Developer Journey — First Install to First Run

```
1. `pip install -e .` (from cloned repo)
2. `cp .env.example .env` -> paste GROQ_API_KEY
3. `anvil init my_agent`
     -> scaffolds a new agent folder: my_agent/agent.py, my_agent/tools.py, my_agent/anvil.config.yaml
4. Developer edits tools.py:
     -> writes a Python function
     -> decorates with @tool, adds docstring + Pydantic param schema
5. Developer edits agent.py:
     -> imports their tools
     -> instantiates AgentConfig(name=..., planner_model=..., executor_model=...)
     -> instantiates AgentRunner(config, tools=[...])
6. `anvil run my_agent "some task in plain English"`
     -> OR programmatically: `runner.run("some task in plain English")`
7. Output streams to terminal (rich-formatted, verbose by default for first-run friendliness)
8. On completion: trace saved to `.anvil/runs/{run_id}.json`
9. `anvil trace {run_id}` -> re-prints a past run's trace human-readably
```

This exact sequence is what the README quickstart section must walk through, in this order, with no skipped steps.

---

## 2. CLI Command Surface

| Command | Behavior |
|---|---|
| `anvil init <agent_name>` | Scaffolds a new agent directory from a template (agent.py, tools.py, anvil.config.yaml). Fails loudly if directory already exists. |
| `anvil run <agent_name> "<task>"` | Loads the agent's config + tools, instantiates `AgentRunner`, calls `.run(task)`. Streams trace to stdout unless `--quiet`. |
| `anvil run <agent_name> "<task>" --verbose` | Same as above, with full tool-call inputs/outputs printed live (default is already fairly verbose — this is the "everything" mode). |
| `anvil run <agent_name> "<task>" --quiet` | Suppresses live trace, only prints final status + trace file path. |
| `anvil trace <run_id>` | Reads `.anvil/runs/{run_id}.json` and re-renders it via the same `rich` formatting used live. |
| `anvil trace --list` | Lists past run IDs with task summary + status, most recent first. |

No other top-level commands in v1 (no `anvil deploy`, no `anvil serve` — those are explicitly out of scope per PRD §4).

---

## 3. Internal Execution Flow — `AgentRunner.run(task)`

This is the core loop every task goes through, and it must be implemented exactly as this sequence — no steps skipped, no reordering:

```
START
  |
  v
[1] Load relevant memory
    - MemoryStore.recall(query=task, k=config.memory_top_k, collection="semantic")
    - Also recall from "episodic" if this is a continuation of a prior incomplete run (not v1 — noted as future work)
  |
  v
[2] Planner.generate_plan(task, tools=registry.all(), memory=recalled_memories)
    -> returns Plan (ordered list of Step objects, each with id, description, tool_hint, depends_on, status="pending")
  |
  v
[3] FOR EACH Step in Plan (sequential, respecting depends_on):
      |
      v
    [3a] Executor.run_step(step)
         -> resolves tool_hint to actual Tool via ToolRegistry
         -> calls GroqClient.chat_with_tools(...) to get the actual tool call + args
         -> executes the tool function
         -> captures StepResult (output, exception if any, duration)
      |
      v
    [3b] QualityEnforcer.rule_check(step_result)  [ALWAYS RUNS]
         -> checks: no exception, non-empty output, matches expected shape
      |
      v
    [3c] IF step.rubric is set: QualityEnforcer.llm_rubric_check(step_result, step.rubric)  [CONDITIONAL]
      |
      v
    [3d] IF rule_check FAILS or (rubric set AND llm_rubric_check FAILS):
             -> step.status = "failed"
             -> SelfHealingEngine.handle_failure(step, failure_context)
                  -> re-invokes either:
                     (a) Executor.run_step(step) again with failure_context appended [same step retry], or
                     (b) Planner.generate_plan(...) for just the failed step + downstream steps [partial re-plan]
                  -> decision (a) vs (b) is based on failure type:
                     - tool execution error (exception) -> (a) same-step retry
                     - quality/rubric failure (ran fine, but wrong) -> (b) partial re-plan
                  -> increments retry count; if retry count > config.max_retries -> step.status = "failed", ABORT plan
         ELSE:
             -> step.status = "success"
             -> MemoryStore.remember(step_result summary, metadata, collection="episodic")
      |
      v
    [3e] Move to next Step (or ABORT if max_retries exceeded on this step)
  |
  v
[4] All Steps done (or aborted)
  |
  v
[5] Tracer.finalize_and_write(run_id) -> writes .anvil/runs/{run_id}.json
  |
  v
[6] Episodic memory for this run is either archived (if agent code explicitly called remember(..., collection="semantic") during the run) or cleared
  |
  v
END -> returns final AgentResult(status, output_summary, trace_path)
```

---

## 4. Failure / Abort Conditions (Explicit)

| Condition | Behavior |
|---|---|
| A Step exceeds `max_retries` | Plan execution aborts. `final_status = "failed"`. Trace still written with all steps up to the failure point. |
| Groq API returns a non-retryable error (e.g. invalid API key, 401) | Immediate abort, no self-heal attempted (self-heal only applies to task-logic failures, not auth/config failures). Raises `ConfigError` to the caller. |
| Tool not found for a `tool_hint` the Planner produced | Treated as a rule_check failure on that step (not a crash) — triggers SelfHealingEngine partial re-plan, since this usually means the Planner hallucinated a tool name and needs to be shown the actual tool list again. |
| `run_shell_command` called without `allow_shell_tool=True` | Tool raises `PermissionError` immediately, surfaced as a rule_check failure — same self-heal path as above. |

---

## 5. Example Agent Flows

**Research Agent** (`anvil run research_agent "What caused the 2008 financial crisis?"`):
```
Plan -> [search topic] -> [read top results] -> [remember key facts] -> [synthesize cited answer]
```

**Scaffold Agent** (`anvil run scaffold_agent "Build a Flask API with a /health endpoint"`):
```
Plan -> [plan file structure] -> [write app.py] -> [write requirements.txt] -> [quality check: files exist + app.py is valid Python]
```

Both flows go through the exact same `AgentRunner.run()` loop in §3 — the only difference is the tools registered and the system prompt/persona. This is the point of the framework: one loop, many agents.
