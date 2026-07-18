# Implementation Plan — Anvil
### Phased Build Sequence

**Doc status:** Draft v1
**How to use this doc:** Build strictly in this order. Each phase has a "done when" checkpoint — do not start the next phase until the current one's checkpoint is met. This prevents the common failure mode of building Planner/Executor logic against tools or memory APIs that don't exist yet or change shape later.

---

## Phase 0 — Repo Scaffold
- Create repo structure exactly as specified in TRD §3.
- `pyproject.toml` with dependencies pinned per TRD §2.
- `LICENSE` (MIT), `.env.example`, `anvil.config.example.yaml`.
- Empty `__init__.py` files establishing the package structure.
- Basic `pytest` config (`pytest.ini` or `pyproject.toml [tool.pytest.ini_options]`) pointing at `tests/`.
- **Done when:** `pip install -e .` succeeds from a clean clone, `pytest` runs (even with zero tests) with no import errors.

## Phase 1 — Tool System
- `anvil/tools/base.py`: `Tool` base, `@tool` decorator, Pydantic-schema-based param validation.
- `anvil/tools/registry.py`: `ToolRegistry` — register, collision detection, `to_groq_schema()`.
- `anvil/tools/builtin/`: `read_file`, `write_file`, `run_shell_command` (sandboxed per TRD §6), `web_search` stub.
- `tests/test_tools.py`: registration, schema validation, collision detection, sandboxing behavior for shell tool.
- **Done when:** a hand-written test agent can register 3+ tools (including a custom one) with zero framework errors, and `to_groq_schema()` output is verified against Groq's expected tool-call JSON shape.

## Phase 2 — Memory Layer
- `anvil/memory/store.py`: `MemoryStore` wrapping ChromaDB `PersistentClient`, per TRD §7 / Backend Schema §2.
- `remember()` and `recall()` for both episodic and semantic collections.
- `tests/test_memory.py`: write/read round-trip, top-k recall correctness, episodic-to-semantic promotion, using `tmp_path` (never real `.anvil/chroma/`).
- **Done when:** memory round-trips correctly in isolation, with no dependency yet on Planner/Executor.

## Phase 3 — Groq LLM Client
- `anvil/llm/groq_client.py`: `GroqClient.chat()`, `chat_with_tools()`, retry/backoff per TRD §8.
- API key resolution logic (constructor > env var > `ConfigError`).
- `conftest.py`: shared mocked-Groq-response fixtures so every later test suite can reuse them without hitting the real API.
- **Done when:** a mocked call to `chat_with_tools()` returns a well-formed tool-call response the Executor (built next) can consume, with zero live API calls required.

## Phase 4 — Core Data Models
- `anvil/core/models.py`: `Plan`, `Step`, `StepResult`, status enums — as plain dataclasses/Pydantic models, JSON-serializable (needed by both Planner output and Tracer).
- **Done when:** `Plan`/`Step` objects serialize to/from the JSON shape defined in Backend Schema §4 with a round-trip test.

## Phase 5 — Planner
- `anvil/core/planner.py`: `Planner.generate_plan(task, tools, memory) -> Plan`.
- Prompts the LLM (via `GroqClient.chat()`) to produce a plan, parses response into `Plan`/`Step` objects, validates shape (fails loudly on malformed LLM output rather than passing bad data downstream).
- `tests/test_planner.py`: given a mocked LLM response, verify correct `Plan` construction; given a malformed response, verify a clear parse error, not a silent bad object.
- **Done when:** Planner reliably turns a mocked LLM text response into a valid `Plan` object, and rejects invalid ones with a clear error.

## Phase 6 — Executor
- `anvil/core/executor.py`: `Executor.run_step(step) -> StepResult`.
- Resolves `step.tool_hint` against `ToolRegistry`, calls `GroqClient.chat_with_tools()`, executes the resolved tool function, captures output/exception/duration into `StepResult`.
- `tests/test_executor.py`: successful tool execution, tool-not-found case, tool exception case.
- **Done when:** Executor runs a single Step end-to-end against a mocked LLM + a real (test) tool function, producing a correct `StepResult` in all three cases above.

## Phase 7 — QualityEnforcer
- `anvil/core/quality.py`: `rule_check()` (always runs) and `llm_rubric_check()` (opt-in via `step.rubric`), per TRD §5.
- `tests/test_quality.py`: rule_check pass/fail cases, rubric check pass/fail (mocked LLM grading call).
- **Done when:** both check types independently return correct pass/fail against constructed `StepResult` fixtures.

## Phase 8 — SelfHealingEngine
- `anvil/core/self_heal.py`: `handle_failure(step, failure_context)` — same-step retry vs. partial re-plan branching logic per App Flow §3/§4, retry counting against `max_retries`.
- `tests/test_self_heal.py`: exception-triggered retry (same-step path), quality-failure-triggered retry (re-plan path), max-retries-exceeded abort path.
- **Done when:** all three branches produce the correct next action and correctly abort after `max_retries`.

## Phase 9 — AgentRunner (Wiring Everything Together)
- `anvil/core/runner.py`: `AgentRunner.run(task) -> AgentResult`, implementing the exact sequence from App Flow §3, steps [1] through [6].
- Integrates Tracer (Phase 10, build alongside) for live + final trace output.
- **Done when:** a full mocked run (mocked Groq responses throughout) executes a multi-step Plan end-to-end, including at least one induced failure that triggers self-healing, and produces a correct final `AgentResult` + trace file.

## Phase 10 — Tracing
- `anvil/tracing/tracer.py`: `Trace` object, live `rich`-formatted output per UI/UX Brief §3, JSON writer per Backend Schema §4.
- **Done when:** trace JSON output validates against the schema exactly, and live verbose output visually matches the UI/UX Brief §3 example structure.

## Phase 11 — CLI
- `anvil/cli/main.py`: `init`, `run`, `trace` commands per App Flow §2, using `click` + `rich`.
- **Done when:** all CLI commands work against a real (non-mocked) local setup with a valid `GROQ_API_KEY`, for at least one example agent.

## Phase 12 — Example Agent: Research Agent
- `examples/research_agent/`: agent + tools (`web_search`, note in README whether it's wired to a real search API or a stub for demo purposes) implementing the flow in App Flow §5.
- **Done when:** `anvil run research_agent "<question>"` produces a coherent, cited answer end-to-end using real Groq calls.

## Phase 13 — Example Agent: Scaffold Agent
- `examples/scaffold_agent/`: agent + tools implementing the flow in App Flow §5 (deliberately smaller in scope than ZAIRE's actual Engineer Mode, per PRD §7.6).
- **Done when:** `anvil run scaffold_agent "Build a Flask API with a /health endpoint"` produces working, syntactically valid files on disk end-to-end.

## Phase 14 — Documentation
- `README.md` per UI/UX Brief §4 structure exactly.
- `docs/architecture.md`, `docs/writing_a_tool.md`, `docs/writing_an_agent.md`, `docs/memory_guide.md`, `docs/faq.md`.
- Record/paste a real terminal output example (from an actual example-agent run, not a fabricated one) into the README.
- **Done when:** a person with no prior context can go from clean clone to a successful `anvil run` using only the README, with no undocumented steps.

## Phase 15 — Polish & Release
- Run full `pytest` suite, confirm ≥85% coverage on `anvil/core/` per TRD §10.
- `CHANGELOG.md` started.
- Tag `v0.1.0`, push public repo.
- **Done when:** repo is public, README is the front page, both example agents work from a completely clean environment, and the "20-30 stars" success metric (PRD §8) is a matter of organic sharing from here, not further building.

---

## Explicit Ordering Rationale (So the Sequence Isn't Reordered by Mistake)

Tools (Phase 1) and Memory (Phase 2) are built before the LLM client (Phase 3) because the Executor and Planner need real objects to call, not stubs — building the LLM client third means the mocked-response fixtures in Phase 3 can already be typed against real `Tool` and `MemoryStore` shapes. Core data models (Phase 4) come next, before Planner/Executor, because both of the latter produce/consume `Plan`/`Step`/`StepResult` — building those two before the shared data model they depend on would guarantee rework. QualityEnforcer and SelfHealingEngine (Phases 7-8) depend on `StepResult` from Executor (Phase 6), so they cannot come earlier. `AgentRunner` (Phase 9) is deliberately last among the core pieces because it's pure wiring — it should have nothing left to design by the time it's built, only integration.
