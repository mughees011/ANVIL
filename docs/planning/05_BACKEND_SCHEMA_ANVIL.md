# Backend / Data Schema — Anvil
### Storage, Data Models & Auth

**Doc status:** Draft v1
**Scope note:** Anvil has no server, no relational database, and no multi-user auth — it's a local-first library that runs in a single developer's process. This doc defines the equivalent for that context: what gets persisted, where, in what shape, and how the one real "credential" (the Groq API key) is handled. This replaces a traditional tables/columns schema with the actual data model Anvil uses.

---

## 1. What Gets Persisted, and Where

| Data | Location | Format | Lifetime |
|---|---|---|---|
| Vector memory (episodic + semantic) | `.anvil/chroma/` | ChromaDB's own on-disk format (SQLite + Parquet internally, managed by ChromaDB) | Semantic: indefinite. Episodic: cleared at end of each run unless explicitly promoted to semantic. |
| Run traces | `.anvil/runs/{run_id}.json` | JSON (schema in §4) | Indefinite, user-managed (not auto-pruned in v1). |
| Agent config | `{agent_dir}/anvil.config.yaml` | YAML (schema in §3) | Source-controlled by the user, part of their agent's repo. |
| Sandbox scratch space (shell tool only) | `.anvil/sandbox/{run_id}/` | Plain files, whatever the shell command produces | Deleted at end of run (v1 default — configurable to persist for debugging). |
| Secrets (Groq API key) | `.env` (gitignored) | `GROQ_API_KEY=...` | User-managed, never written by Anvil itself. |

`.anvil/` is the single top-level data directory Anvil owns, analogous to `.git/` — the README must instruct users to add it to `.gitignore` except for `anvil.config.yaml` files, which live outside `.anvil/` (in the agent's own directory) since those ARE meant to be committed.

---

## 2. ChromaDB Collection Schema

Two collections per agent, named by convention (not configurable, to keep discovery simple):

**`{agent_name}_episodic`**
| Field | Type | Notes |
|---|---|---|
| `id` | string (UUID) | ChromaDB document ID |
| `document` | string | The actual remembered text |
| `embedding` | vector (auto-generated) | Via ChromaDB default embedding fn, not user-supplied |
| `metadata.run_id` | string | Which run this memory belongs to |
| `metadata.step_id` | string | Which step produced it |
| `metadata.timestamp` | ISO8601 string | When it was written |
| `metadata.memory_type` | `"episodic"` | Constant, used for filtering |

**`{agent_name}_semantic`**
| Field | Type | Notes |
|---|---|---|
| `id` | string (UUID) | ChromaDB document ID |
| `document` | string | The remembered fact/summary |
| `embedding` | vector (auto-generated) | Same embedding fn as episodic |
| `metadata.promoted_from_run_id` | string \| null | Set if this came from an episodic memory the agent explicitly promoted |
| `metadata.timestamp` | ISO8601 string | When it was written |
| `metadata.memory_type` | `"semantic"` | Constant, used for filtering |
| `metadata.tags` | list[string] (optional) | Agent-author-defined, for future filtered recall |

---

## 3. Agent Config Schema (`anvil.config.yaml`)

```yaml
name: research_agent
planner_model: "<groq-model-slug>"      # see TRD §4 — verify current slug at build time
executor_model: "<groq-model-slug>"
max_retries: 3
memory_top_k: 5
allow_shell_tool: false
shell_timeout_seconds: 30                # only relevant if allow_shell_tool: true
```

This maps 1:1 to the `AgentConfig` Pydantic model in the TRD (§4) — the YAML is just the on-disk representation. `pydantic` validates on load; an invalid/missing required field raises a `ConfigError` at `anvil run` time, before any Groq call is made (fail fast, don't burn an API call on a broken config).

---

## 4. Trace JSON Schema (`.anvil/runs/{run_id}.json`)

This is the canonical schema — identical to the one specified in TRD §9, repeated here as the single data-model source of truth:

```json
{
  "run_id": "string (uuid)",
  "agent_name": "string",
  "task": "string",
  "plan": [
    {
      "step_id": "string",
      "description": "string",
      "status": "pending | success | failed | retried"
    }
  ],
  "steps": [
    {
      "step_id": "string",
      "tool_calls": [
        { "tool": "string", "input": {}, "output": {} }
      ],
      "quality_check": {
        "rule_check": "pass | fail",
        "llm_rubric_check": "pass | fail | null"
      },
      "retries": "integer"
    }
  ],
  "final_status": "success | failed",
  "started_at": "ISO8601 string",
  "ended_at": "ISO8601 string"
}
```

No database engine, no ORM — this is written and read with plain `json.dump`/`json.load`. Explicitly not over-engineered with SQLite for v1; if trace volume becomes a real problem later, that's a v2 concern, not v1.

---

## 5. Authentication / Credential Flow

There is no user-authentication system in Anvil — it's a local, single-user library. The only credential is the Groq API key:

```
1. User signs up for Groq, gets an API key (external to Anvil, out of scope for this doc).
2. User places it in .env as GROQ_API_KEY=... (never committed — .env is in .gitignore from anvil init).
3. GroqClient resolution order (per TRD §8):
   a. Explicit constructor param, if the agent author passed one directly (rare, mainly for tests).
   b. GROQ_API_KEY environment variable (the standard path, loaded via python-dotenv).
   c. If neither is present -> raise ConfigError immediately, do not proceed silently.
4. The key is held in memory for the process lifetime only. Anvil never writes the key to
   .anvil/runs/ traces, logs, or any persisted file — trace serialization explicitly excludes
   any field that could contain the raw key.
```

This is the entirety of the "auth flow" — there is no session, no token refresh, no user table, because there is no multi-user concept in v1 (consistent with PRD §4 non-goals).

---

## 7. Trace Dashboard API Schema (Post-Core, Phase 16)

Resolves PRD §7.8 / TRD §13. All endpoints are read-only, served by the optional FastAPI app, bound to `localhost` only.

**`GET /api/runs`** — list summaries (not full traces, keeps this endpoint fast even with hundreds of runs on disk):
```json
[
  {
    "run_id": "string (uuid)",
    "agent_name": "string",
    "task": "string",
    "final_status": "success | failed",
    "started_at": "ISO8601 string"
  }
]
```

**`GET /api/runs/{run_id}`** — full trace, identical shape to the on-disk file. No reshaping:
```
Same schema as .anvil/runs/{run_id}.json, defined in §4 above.
```

**`GET /api/agents/{agent_name}/memory?collection=episodic|semantic&limit=50`** — paginated, most-recent-first browse:
```json
[
  {
    "id": "string (uuid)",
    "document": "string",
    "metadata": { "...": "as defined in §2 for the relevant collection" }
  }
]
```

**Error shape** (consistent across all endpoints):
```json
{ "error": "string (human-readable)", "status_code": "integer" }
```

No other endpoints in v1 — no POST/PUT/DELETE, no run-triggering, no auth. If `run_id` or `agent_name` doesn't exist on disk, return `404` with the error shape above, not a silent empty response.

---

## 8. Explicit Non-Goals for This Schema

- No relational database, no ORM, no migrations system — would be over-engineering for a local single-user library.
- No user accounts, sessions, or roles — not applicable to a CLI tool run by one developer on one machine.
- No encryption-at-rest for `.anvil/chroma/` or trace files in v1 — documented plainly as a known limitation, not silently glossed over. If a future version needs multi-tenant or shared-server use, this section will need a full rewrite, not a patch.
