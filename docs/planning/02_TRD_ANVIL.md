# TRD — Anvil
### Technical Requirements Document

**Doc status:** Draft v1 — resolves all open questions from PRD §9. No guessing left for implementation.

---

## 1. Stack (Exact, Pinned)

| Layer | Choice | Version (min) | Why |
|---|---|---|---|
| Language | Python | 3.11+ | Match ZAIRE's Python agent daemon; structural pattern matching + typing improvements used in core loop. |
| LLM provider | Groq API | `groq` Python SDK ≥ 0.11 | Matches ZAIRE, fast inference, native tool-calling support. |
| Vector memory | ChromaDB | `chromadb` ≥ 0.5 | Matches ZAIRE's existing usage. Persistent local client, no server process. |
| Data validation | Pydantic | v2 (≥ 2.7) | Tool schemas, Plan/Step models, config models — all Pydantic `BaseModel`s. |
| CLI | Typer | ≥ 0.12 | Thin CLI wrapper around `AgentRunner`; auto-generates `--help`. |
| Terminal output | Rich | ≥ 13.7 | Verbose trace printing, colored step status, tables. |
| Env/config | `python-dotenv` + `PyYAML` | latest | `.env` for secrets (`GROQ_API_KEY`), `anvil.config.yaml` for agent config. |
| Testing | `pytest` + `pytest-mock` | latest | All Groq calls mocked in unit tests — CI must run without a live API key. |
| Lint/format | `ruff` | latest | Single tool for lint + format, one config file. |
| Packaging | `pyproject.toml` (PEP 621), `hatchling` build backend | — | Modern packaging, `pip install -e .` for local dev. |
| CI | GitHub Actions | — | `lint` + `test` jobs on push/PR. |

**Explicitly not used:** LangChain, LlamaIndex, or any existing agent framework as a dependency. Anvil's core loop is hand-written — that's the entire point of the project.

---

## 2. Package Structure

```
anvil/
├── pyproject.toml
├── README.md
├── LICENSE                        # MIT
├── .env.example
├── anvil.config.example.yaml
├── src/
│   └── anvil/
│       ├── __init__.py
│       ├── agent.py               # AgentRunner
│       ├── config.py              # Pydantic config models, .env + yaml loader
│       ├── llm/
│       │   ├── __init__.py
│       │   └── groq_client.py     # thin wrapper around groq SDK, retry/backoff
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── registry.py        # @tool decorator, ToolRegistry class
│       │   ├── builtin_fs.py      # read_file, write_file
│       │   └── builtin_shell.py   # run_shell_command (sandboxed, opt-in)
│       ├── memory/
│       │   ├── __init__.py
│       │   └── store.py           # ChromaMemory: remember(), recall()
│       ├── planning/
│       │   ├── __init__.py
│       │   ├── models.py          # Plan, Step (Pydantic)
│       │   └── planner.py         # Planner class
│       ├── execution/
│       │   ├── __init__.py
│       │   └── executor.py        # Executor class
│       ├── quality/
│       │   ├── __init__.py
│       │   ├── checks.py          # rule-based checks
│       │   └── enforcer.py        # QualityEnforcer, orchestrates checks
│       ├── healing/
│       │   ├── __init__.py
│       │   └── self_heal.py       # SelfHealingEngine
│       ├── tracing/
│       │   ├── __init__.py
│       │   └── trace.py           # RunTrace model, JSON writer, Rich printer
│       └── cli/
│           ├── __init__.py
│           └── main.py            # Typer app: `anvil init`, `anvil run`, `anvil trace`
├── examples/
│   ├── research_agent/
│   │   ├── agent.py
│   │   └── README.md
│   └── scaffold_agent/
│       ├── agent.py
│       └── README.md
├── docs/
│   ├── architecture.md
│   ├── first_tool.md
│   ├── first_agent.md
│   ├── memory.md
│   └── faq.md
└── tests/
    ├── test_tools_registry.py
    ├── test_planner.py
    ├── test_memory.py
    ├── test_quality_enforcer.py
    └── test_self_heal.py
```

---

## 3. Core Loop — Exact Control Flow

```
AgentRunner.run(task: str) ->
    1. memory.recall(task, k=config.memory_top_k)           # relevant long-term context
    2. plan = Planner.generate_plan(task, tools, memory_ctx) # -> Plan (list[Step])
    3. for step in plan.steps (respecting depends_on order):
        a. result = Executor.run_step(step, tools)
        b. verdict = QualityEnforcer.check(step, result)
        c. if verdict.failed:
              if step.retry_count < config.max_retries:
                  step = SelfHealingEngine.handle_failure(step, result, verdict)
                  goto (a) with incremented retry_count
              else:
                  mark step FAILED, halt plan (config.halt_on_failure=True default)
        d. memory.remember(f"{step.description} -> {result.summary}", metadata={...})
    4. trace.finalize() -> writes .anvil/runs/{run_id}.json
    5. return AgentResult(status, output_summary, trace_path)
```

Full branching detail (same-step retry vs. partial re-plan) is specified in App Flow §3 — this section is the condensed version for quick reference.

---

## 4. Groq API Integration Details

- **Model selection**: per-agent, set in `AgentConfig.planner_model` / `AgentConfig.executor_model` (separate fields — a cheaper/faster model can drive tool execution while a stronger one plans, mirroring ZAIRE's per-mode model assignment). Default for both: `llama-3.3-70b-versatile`. Framework does not hardcode a model allow-list — it passes the string through as-is, so this doc doesn't go stale as Groq's lineup changes. **Verify the current model slug against Groq's docs at build time.**
- **Function calling**: use Groq's native `tools` parameter (OpenAI-compatible schema). `ToolRegistry.to_groq_schema()` converts registered `Tool` objects to this format.
- **Temperature**: Planner calls use `temperature=0.2` (deterministic-leaning plans). Executor tool-selection calls use `temperature=0` where possible. Both configurable per-agent override.
- **Retries on transient API errors** (429, 5xx): exponential backoff, max 3 attempts, base delay 1s — implemented in `groq_client.py`, separate from `SelfHealingEngine` (that's for *logical* task failures, this is for *transport* failures — see App Flow §4 for the distinction).
- **API key**: read from `GROQ_API_KEY` env var via `.env`. Never logged, never included in trace JSON (see Backend Schema §5).

---

## 5. ChromaDB Integration Details

- **Client type**: `chromadb.PersistentClient(path=".anvil/chroma/")` — one on-disk store per project, subfolders per agent.
- **Collections per agent**: `{agent_name}_episodic`, `{agent_name}_semantic` (naming enforced in `store.py`, not left to the agent author — see Backend Schema §2 for exact field-level schema).
- **Embedding function**: ChromaDB's bundled default (`all-MiniLM-L6-v2` via `onnxruntime`) — no external embedding API call, keeps memory fully local and free.
- **Episodic lifecycle**: written during a run, cleared at the start of the agent's next Task unless explicitly promoted via `memory.remember(..., collection="semantic")`.
- **Recall API**: `memory.recall(query: str, k: int = 5, collection: Literal["episodic","semantic","both"] = "both") -> list[MemoryHit]`.

---

## 6. QualityCheck — Resolved Design

Two check types, both usable per-Step (resolves PRD open question #2):

1. **Rule-based** (`quality/checks.py`) — zero extra LLM cost, always runs. Built-in checks: `no_tool_error`, `output_not_empty`, `output_matches_schema(pydantic_model)`, `file_exists(path)`. Agent authors can register custom rule functions (`Callable[[StepResult], bool]`).
2. **LLM-graded rubric** (opt-in per Step via `Step.rubric: str | None`) — if set, `QualityEnforcer` makes one extra Groq call asking the model to grade the `StepResult` against the rubric text, returns pass/fail + reason. Off by default (keeps cost/latency down); agent authors opt in per-step for steps where correctness is fuzzy (e.g. "is this summary actually useful").

`QualityEnforcer.check()` runs rule-based checks first (fast fail), only invokes the LLM-graded check if all rule-based checks pass and a rubric is set.

---

## 7. SelfHealingEngine — Resolved Design

- Triggered only on QualityCheck failure (not on transport errors — those are handled by `groq_client.py` retry logic, §4).
- `max_retries` configurable per-agent (default 3), tracked per-Step via `Step.retry_count`.
- Repair strategy branches by failure type (see App Flow §3 for the full decision tree):
  - **Tool execution exception** → same-step retry (re-invoke `Executor.run_step` with failure context appended).
  - **Quality/rubric failure** (ran fine, but wrong) → partial re-plan (re-invoke `Planner.generate_plan` for just the failed step + downstream dependents, not the whole Plan).
- If `max_retries` exceeded: Step marked `FAILED`, and per `config.halt_on_failure` (default `True`), the whole run halts and returns a partial trace rather than silently continuing with a broken dependency chain.

---

## 8. Shell Tool Sandboxing — Resolved Design

`run_shell_command` (built-in tool, **disabled by default** — agent author must explicitly enable via `AgentConfig.allow_shell_tool: true`):

- Executes via `subprocess.run(cmd, cwd=jail_dir, timeout=config.shell_timeout_seconds, capture_output=True, shell=False)` — `shell=False` and args passed as a list, never a raw string, to avoid trivial injection.
- `jail_dir`: must be explicitly configured (`AgentConfig.shell_jail_dir`) — framework refuses to run the tool if unset, no silent fallback to cwd.
- `shell_timeout_seconds`: default 30, configurable.
- No attempt at a full OS-level sandbox (no Docker/gVisor) in v1 — documented explicitly in `docs/faq.md` as a known limitation, not hidden. This is the resolved answer to PRD open question #3: safer default, not maximal isolation.

---

## 9. Trace Schema (Reference)

Full canonical schema lives in Backend Schema §4 (single source of truth — do not duplicate/diverge). Summary: each run produces one JSON file containing `run_id`, `agent_name`, `task`, `plan` (list of steps with status), `steps` (tool calls + quality check results + retry counts), `final_status`, and timestamps.

---

## 10. Config File Schema (Reference)

Full schema lives in Backend Schema §3. Summary: `anvil.config.yaml` per agent covers model selection, temperature, retry/halt behavior, memory top-k, and shell tool settings. `.env` holds only `GROQ_API_KEY`.

---

## 11. Testing & CI Requirements

- All Groq API calls mocked via `pytest-mock` fixtures returning canned tool-call JSON — **no test may require a live `GROQ_API_KEY`**.
- Minimum coverage targets: `tools/registry.py`, `planning/planner.py` (plan shape validation), `memory/store.py` (round-trip remember/recall against a temp ChromaDB dir), `quality/enforcer.py`, `healing/self_heal.py` (retry counting + halt behavior).
- GitHub Actions: `lint.yml` (ruff check), `test.yml` (pytest on 3.11 and 3.12 matrix).

---

## 13. Trace Dashboard — Stack & Architecture (Post-Core, Phase 16)

Resolves the scope addition from PRD §7.8. Kept as its own section, deliberately separable — nothing in Phases 1-11 (the core library) depends on any of this.

### 13.1 Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend framework | React 18 + Vite | Fast dev server, matches ZAIRE's frontend stack for consistency across your projects. |
| Language | TypeScript | Catches integration bugs against the trace JSON shape (Backend Schema §4) at compile time. |
| Styling | Tailwind CSS | Matches the existing prototype's dark-glass aesthetic; no custom CSS framework needed. |
| Charts/stats | Recharts | Lightweight, matches PRD's "no heavy dependency" philosophy. |
| Icons | `lucide-react` | Matches the diamond/arrow symbol vocabulary already established in UI/UX Brief §2. |
| Local API server (optional) | FastAPI + `uvicorn` | Only pulled in via the `web` extra (`pip install anvil-agent[web]`) — the core library has zero dependency on this. |

### 13.2 Package Layout Addition

```
anvil/
├── web/
│   ├── frontend/                   # React + Vite + TS app
│   │   ├── src/
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── tailwind.config.js
│   └── backend/
│       └── api.py                  # FastAPI app: serves built frontend + read-only trace API
```

Lives in its own `web/` directory, separate from `src/anvil/` — the Python package that ships to PyPI does **not** bundle the frontend source, only (optionally) the built static files if the `web` extra is installed.

### 13.3 API Server (`web/backend/api.py`)

- `GET /api/runs` — list all trace summaries from `.anvil/runs/` (run_id, agent_name, task, final_status, started_at — not the full trace, keeps the list endpoint fast).
- `GET /api/runs/{run_id}` — full trace JSON for one run, identical shape to the on-disk file (Backend Schema §4) — the API does not reshape or rename fields, it serves the file's contents directly.
- `GET /api/agents/{agent_name}/memory` — read-only browse of that agent's episodic/semantic ChromaDB collections (paginated, top N by recency — not a search endpoint in v1).
- Serves the built frontend's static files at `/`.
- **Read-only.** No POST/PUT/DELETE endpoints in v1 — the dashboard cannot trigger runs, edit traces, or modify memory. This keeps the "local single-user tool" framing honest and avoids needing any auth layer.
- Started via `anvil trace web [--port 8420]` (CLI addition — see App Flow §6). Binds to `localhost` only, never `0.0.0.0`, in v1 — this is a local dev tool, not something meant to be exposed on a network.

### 13.4 Drag-and-Drop Mode (No Server)

The built frontend must work standalone (open `index.html` directly, or serve it with any static file server) with zero backend — trace JSON dropped into the browser is parsed and rendered entirely client-side. This is the fallback that makes the dashboard usable even for someone who doesn't want to `pip install` the `web` extra at all; they can just open the built static site and drop in a trace file a teammate sent them.

---

## 14. Explicit Assumptions Made in This Draft

- Groq model default set to `llama-3.3-70b-versatile` — confirm this is still the model you want; Groq's available models may have changed since this was drafted, and this should be re-verified at build time rather than trusted from this doc.
- No async support in v1 core (`Executor` runs steps synchronously, sequentially) — flagged as a fast-follow, not blocking launch. (The FastAPI dashboard server in §13 is async internally, but that's independent of the core Executor's sync design.)
- PyPI publishing intentionally deferred; `pip install -e .` from GitHub is the v1 install path.
- Dashboard port default (`8420`) is arbitrary — change freely, just keep it documented consistently across the CLI help text and README once built.
