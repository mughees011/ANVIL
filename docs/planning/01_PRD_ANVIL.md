# PRD — Anvil
### A Local-First Python Agent Framework (Tool-Calling · Memory · Multi-Step Planning)

**Doc status:** Draft v1
**Author:** Mughees
**Placeholder name:** "Anvil" — rename freely, all docs use this token consistently so find-and-replace is safe.

---

## 1. What This Is

Anvil is a small, open-source Python framework for building AI agents that can:
- call tools/functions reliably,
- remember things across turns and sessions (local vector memory via ChromaDB),
- break a goal into a multi-step plan, execute it, check its own work, and self-correct.

It is **not** a chatbot UI, not a SaaS product, and not a LangChain-style everything-framework. It is the orchestration core — the part that decides *what to do next* — generalized out of the ZAIRE Engineer Mode backend (`engineer_specialist.py`) so it can run standalone, get open-sourced, and be reused in other projects (including future ZAIRE modes).

**Positioning line for the repo README / portfolio:**
> "I built my own agent orchestration layer" — not "I used LangChain."

---

## 2. Problem Statement

Existing agent frameworks (LangChain, CrewAI, AutoGPT-style tools) are either:
- too heavy/abstracted (you fight the framework more than you use it),
- too opinionated about memory/vector store choice,
- or too focused on chat rather than **planned, multi-step execution with self-verification**.

ZAIRE's Engineer Mode already solved a real version of this problem for one narrow domain (scaffolding software projects). Anvil takes that proven design — planner → executor → quality check → self-heal loop — and generalizes it so it isn't tied to "generate a codebase," but to **any** tool-using, multi-step task.

---

## 3. Goals

1. Provide a minimal, readable core loop: **Plan → Act (tool call) → Observe → Check → Retry/Heal → Done.**
2. Local-first memory: ChromaDB running locally, no hosted vector DB dependency required.
3. Groq as the only LLM provider for v1 (matches ZAIRE, keeps scope tight, fast inference for iteration).
4. Tool-calling that is explicit and typed — no magic, the agent author defines tools with a schema.
5. Ship with 2 working example agents that prove the framework in different domains (not just two flavors of the same demo).
6. Documentation good enough that a stranger can install, run an example, and build their own tool in under 15 minutes.
7. Get this to a public GitHub repo with a real README, real examples, real tests — worth 20-30 stars on its own merit.

## 4. Non-Goals (v1 Core)

- Multi-provider LLM support (OpenAI/Anthropic/local models) — explicitly deferred.
- Multi-agent collaboration / agent-to-agent messaging — not v1. Single-agent, multi-step only.
- A hosted/cloud, multi-user, or always-on server product. Anvil's core remains a library, imported like any Python package — the optional Trace Dashboard (§7.8) is a local, single-user visualization tool for that library's output, not a hosted service.
- Distributed execution, queues, or async job workers.
- Fine-tuning or training anything. Anvil orchestrates a frontier model via API; it doesn't train one.
- Windows-specific packaging (ZAIRE is the Windows desktop app; Anvil is the reusable engine, OS-agnostic).

**Revision note:** the original draft of this section listed "dashboard or UI" as fully out of scope. That's been narrowed, not reversed — see §7.8: a local trace-visualization dashboard is now in scope, but explicitly as a *post-core, optional companion tool* (built after Phases 1-11 of the core framework are done), not a v1-blocking feature and not a hosted product.

---

## 5. Target Users

- Developers who currently reach for LangChain out of habit and find it too heavy for a focused agent.
- Builders who want a hackable core they can read end-to-end in one sitting (~1,500-3,000 lines, not tens of thousands).
- Mughees's own future self / future ZAIRE modes — Anvil should be usable as a dependency inside ZAIRE later, replacing the current in-app-only engineer_specialist logic.

---

## 6. Core Concepts (Vocabulary Used Consistently Across All Docs)

| Term | Definition |
|---|---|
| **Agent** | A configured instance of the framework: a system prompt/persona, a toolset, a memory namespace, and a model config. |
| **Tool** | A Python function exposed to the agent with a name, description, and JSON-schema-typed parameters. |
| **Task** | A single user-issued goal, e.g. "Set up a REST API with auth." |
| **Plan** | An ordered list of Steps produced by the Planner for a given Task. |
| **Step** | One unit of work in a Plan — usually maps to one or more tool calls. |
| **Memory** | Persistent, retrievable context stored in ChromaDB — split into short-term (this task) and long-term (this agent, across tasks). |
| **QualityCheck** | A post-step or post-plan verification pass that decides pass/fail against explicit criteria. |
| **SelfHeal** | The retry/repair loop triggered when a QualityCheck fails — re-plans or re-executes the failed step with the failure context added. |

---

## 7. Feature List (Detailed)

### 7.1 Core Orchestration Loop
- `Planner`: takes a Task + available Tools + relevant Memory -> produces a structured `Plan` (ordered `Step` objects with dependencies).
- `Executor`: runs one `Step` at a time, resolves which Tool(s) it needs, calls them, captures results.
- `QualityEnforcer`: runs configurable checks after each Step (or after the full Plan, configurable) — e.g. "did the tool call return an error," "does output match expected shape," or an LLM-graded rubric check.
- `SelfHealingEngine`: on QualityCheck failure, re-invokes the Planner or Executor with the failure appended to context, up to a max retry count (configurable, default 3).
- `AgentRunner`: the top-level object a user instantiates — wires Planner + Executor + QualityEnforcer + SelfHealingEngine + Memory + Tools together and exposes a single `.run(task: str)` entrypoint.

### 7.2 Tool-Calling
- Tool registration via a decorator: `@tool` with docstring-derived description + explicit Pydantic schema for params.
- Tool registry: agent is instantiated with a list of tools; framework validates no name collisions, validates schemas at startup (fail fast, not at call time).
- Native Groq function-calling format used under the hood — framework translates internal Tool objects to/from Groq's tool-call JSON schema.
- Tool execution sandboxing: tools run in-process by default (v1). Interface is designed so a future sandboxed/subprocess executor can be swapped in without changing the Tool author's code.
- Built-in tools shipped with the framework (agent authors can opt in): `read_file`, `write_file`, `run_shell_command` (explicit opt-in, off by default for safety), `web_search` stub (interface only, no key bundled).

### 7.3 Memory (ChromaDB, local)
- Local ChromaDB instance (persistent client, on-disk, no server process required for v1 — matches ZAIRE's existing ChromaDB usage pattern).
- Two collections per agent: `{agent_name}_episodic` (short-term, one Task's worth of Step results, cleared/archived after Task completion) and `{agent_name}_semantic` (long-term, facts/summaries the agent explicitly decides to persist).
- Retrieval is similarity-search based, top-k configurable, injected into Planner and Executor prompts as context.
- Explicit `memory.remember(text, metadata)` and `memory.recall(query, k)` API — no automatic/implicit writes the user can't see or control.
- Embeddings: use ChromaDB's default local embedding function for v1 (no external embedding API call required — keeps "local-first" honest).

### 7.4 Multi-Step Task Planning
- Plans are explicit, inspectable objects (not just chain-of-thought text) — a `Plan` is a list of `Step` dataclasses with `id`, `description`, `tool_hint`, `depends_on`, `status`.
- Plans can be partially re-generated (only failed/downstream steps), not always fully re-planned from scratch — this mirrors ZAIRE's SelfHealingEngine behavior.
- Support for sequential plans in v1. (Parallel/independent-step execution is a fast-follow, not v1 — noted as an explicit open question in the TRD.)

### 7.5 Observability / Debuggability
- Every run produces a structured trace (JSON): Task -> Plan -> each Step's tool calls, inputs, outputs, QualityCheck verdicts, retries.
- A `--verbose` / logging mode that prints the trace human-readably to stdout as it runs (important for a demo/GIF in the README).
- Trace is saved to disk per run (`.anvil/runs/{run_id}.json`) so past runs can be inspected or replayed.

### 7.6 Example Agents (Ship With the Repo)
Two agents, deliberately in **different domains** so the framework's generality is obvious at a glance:
1. **Research Agent** — given a question, searches (stubbed/mock or real web search tool), takes notes into memory, synthesizes a cited answer. Demonstrates memory + planning without any code-generation overlap with ZAIRE.
2. **Scaffold Agent** — a deliberately small, generalized version of ZAIRE's Engineer Mode: given "build me a Flask API with a /health endpoint," plans file structure, writes files via the `write_file` tool, and self-checks that the files exist and are syntactically valid. This is the direct "proof this came from ZAIRE" example, but is intentionally scoped much smaller than ZAIRE's actual Engineer Mode.

### 7.7 Documentation & Packaging
- `README.md`: what it is, 60-second quickstart, one terminal GIF/asciinema-style output, architecture diagram (ASCII or simple image), link to full docs.
- `docs/`: architecture doc, "write your first tool" guide, "write your first agent" guide, memory guide, FAQ.
- Installable via `pip install -e .` locally for v1; PyPI publish is a stretch goal, not required for launch.
- MIT License (default assumption — flag if you want something else, e.g. Apache-2.0).
- Test suite (`pytest`) covering: tool registry validation, planner output shape, memory read/write, self-heal retry logic (mocked Groq responses — tests should not require a live API key to run in CI).

### 7.8 Trace Dashboard (Web UI) — Post-Core Companion Tool

A local, single-user web dashboard for visualizing run traces — the productized version of the prototype already built (Overview, Runs, Plan & Trace, Memory, Architecture views). Explicitly scoped as **optional and built after the core framework is complete** (Implementation Plan Phase 16, not part of Phases 1-11) — the core library must work standalone with zero dependency on this dashboard ever being built or running.

- **Two data-access modes, both supported:** (1) drag-and-drop a trace JSON file directly in the browser — pure client-side, no server required, works from a static build; (2) `anvil trace web` starts a local FastAPI server that auto-reads from `.anvil/runs/` and serves live data. Both modes render through the same UI components — the dashboard doesn't know or care which mode supplied the data.
- **Views:** Overview (aggregate stats — successful runs, self-heals, tool calls, memory entries; latest run summary), Runs (list/browse past runs), Plan & Trace (step-by-step breakdown of one run, mirroring the CLI's verbose trace structure), Memory (browse episodic/semantic entries for an agent), Architecture (the same diagram from UI/UX Brief §5, rendered rather than ASCII).
- **Explicitly not in scope for this feature:** authentication, multi-user access, remote/hosted deployment, editing or re-running tasks from the dashboard (read-only visualization only, v1).
- Full technical spec: TRD §13, Backend Schema §7, App Flow §6, UI/UX Brief §7.

---

## 8. Success Metrics

- **Functional:** both example agents run end-to-end from a clean clone + `pip install -e .` following only the README.
- **Traction:** repo is public, has a real README, and organically reaches 20-30 GitHub stars without paid promotion.
- **Reusability proof:** at least a sketch/plan exists (even if not fully implemented in v1) for how ZAIRE's actual Engineer Mode would import Anvil instead of its in-app-only logic.
- **Readability:** a new contributor can read the core loop (`Planner` -> `Executor` -> `QualityEnforcer` -> `SelfHealingEngine`) end to end and understand it without needing the ZAIRE codebase for context.

---

## 9. Open Questions Carried Into the TRD

These are flagged here, and the TRD must resolve all three with a concrete decision (no ambiguity left for implementation):

1. **Groq model selection** — does Anvil pick one fixed model, or expose model choice per-agent (mirroring ZAIRE's per-mode model assignment)?
2. **QualityCheck implementation** — rule-based checks only (fast, deterministic, no extra LLM call) vs. LLM-graded rubric checks (more flexible, costs a call) vs. both, configurable per Step.
3. **Sandboxing of `run_shell_command`** — in-process with no isolation (fast, dangerous) vs. subprocess with a timeout and working-directory jail (safer, still not a full sandbox) for v1.

---

## 10. Explicit Assumptions Made in This Draft

- Framework name "Anvil" is a placeholder pending your decision.
- License assumed MIT unless you specify otherwise.
- "20-30 GitHub stars" from your original framing is treated as the success bar, not a stretch target.
- Two example agents were chosen to intentionally diverge from ZAIRE's exact use case (code scaffolding) so the framework doesn't read as "ZAIRE lite" — confirm if you'd rather both examples lean into dev-tooling use cases instead.
