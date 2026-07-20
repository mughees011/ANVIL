# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2026-07-20

### Added

**Core Engine (Phases 1–11)**
- `AgentRunner` — the main execution loop: memory recall → plan → execute → quality check → self-heal → write trace.
- `Planner` — LLM-backed task decomposition via Groq. Outputs a strongly-typed `Plan` with uniquely-identified `Step` objects and explicit string-based `depends_on` references.
- `Executor` — resolves each plan step into a concrete tool call, executes the tool, and captures a `StepResult`.
- `ToolRegistry` — decorator-based `@tool` registration with Pydantic parameter schema validation.
- `QualityEnforcer` — deterministic rule checks (no crash, non-empty output) plus optional LLM rubric scoring.
- `SelfHealingEngine` — retry loop with configurable `max_retries`; branches between same-step retry (on tool crash) and partial re-plan (on quality failure). Tracks `retry_count` correctly across re-planned steps.
- `MemoryStore` — ChromaDB-backed local vector store with `episodic` (per-run) and `semantic` (persistent) collections.
- `RunTrace` — structured execution trace writer (`JSON`) with live Rich terminal output (color vocabulary from UI/UX spec).
- `AgentConfig` — Pydantic-validated YAML configuration with `ConfigError` on missing or invalid values.
- `load_config()` — resolves `.env` by walking upward with `find_dotenv()` so the API key is found regardless of current working directory.
- `get_project_root()` — walks upward from `CWD` to find `pyproject.toml`, anchoring `.anvil/runs/` and `.anvil/chroma/` to one consistent project-root location.
- Groq LLM client with JSON-mode tool-calling and structured output.
- CLI commands: `anvil run`, `anvil trace`, `anvil trace --list`, `anvil init`.

**Planner robustness**
- System prompt explicitly enforces `id` (string, e.g. `"step_1"`) and `depends_on` (list of prior step IDs, never integers).
- `_parse_plan` raises a descriptive `PlannerOutputError` if `depends_on` contains any non-string value, surfacing the exact malformed field rather than a raw Pydantic traceback.

**Example Agents (Phases 12–13)**
- `research_agent` — Wikipedia search tool, recall + remember pattern.
- `scaffold_agent` — file I/O + shell tool (jail-dir guarded), generates and validates project scaffolds.

**Trace Dashboard (Phase 16)**
- FastAPI backend serving the `.anvil/runs/` directory as a REST API.
- React frontend with dark-glass design: Overview, Runs list, Plan & Trace view, Memory tab.

**Documentation (Phase 14)**
- `README.md` — one-line pitch, 60-second quickstart, terminal output example, ASCII architecture diagram, links to docs.
- `docs/architecture.md` — component-by-component breakdown of the execution loop.
- `docs/memory.md` — episodic vs. semantic memory guide.
- `docs/writing_a_tool.md` — how to write and register a tool.
- `docs/writing_an_agent.md` — how to configure and run an agent.
- `docs/faq.md` — common questions vs. LangChain/AutoGen, LLM provider, dashboard.

### Fixed

- **Self-heal retry counter** — verbose trace no longer shows `(attempt 0/3)` on every retry; now correctly shows `1/3`, `2/3`, `3/3`.
- **`.env` resolution** — `load_config()` now uses `find_dotenv(usecwd=True)` so `GROQ_API_KEY` is found when `anvil run` is invoked from a subdirectory.
- **`.anvil/` path anchoring** — `RunTrace` and `MemoryStore` now resolve their storage paths relative to `get_project_root()` rather than `os.getcwd()`, preventing split `.anvil/` directories across different invocation paths.

### Testing

- 51 passing tests across all modules (`test_config`, `test_executor`, `test_memory`, `test_paths`, `test_planner`, `test_quality_enforcer`, `test_runner`, `test_self_heal`, `test_tools_registry`).
- Regression tests for `.env` upward search and `.anvil/` project-root anchoring.

---

## [Unreleased]

_Nothing yet._
