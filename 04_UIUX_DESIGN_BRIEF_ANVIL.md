# UI/UX Design Brief — Anvil
### Developer Experience & Visual Presentation

**Doc status:** Draft v1
**Scope note:** Anvil has no graphical UI — it's a CLI + library. "UI/UX" here means the **developer experience surface**: terminal output design, README/docs visual structure, and trace presentation. This is specified explicitly so output formatting isn't left to chance during implementation (same principle as a GUI design brief — nothing should be "designed" ad hoc by whoever writes the code).

---

## 1. Design Principles

1. **Legible over flashy.** This isn't ZAIRE's plasma-orb HUD — it's a terminal tool read by developers deciding whether to trust and adopt it. Clarity wins over cleverness.
2. **Show the reasoning, not just the result.** The whole pitch of Anvil is "you can see what the agent is doing." Verbose-by-default output is a feature, not a debug leftover.
3. **Consistent color vocabulary**, reused across CLI output, trace files (when rendered), and docs — so a user's eye learns the system once.

---

## 2. Terminal Output — Color & Symbol Vocabulary

Uses `rich` styles. This table is authoritative — the CLI implementation must use exactly these mappings, not ad hoc colors per feature:

| Meaning | Color | Symbol prefix |
|---|---|---|
| Info / plan step starting | Cyan | `→` |
| Tool call in progress | Dim white | `…` |
| Success | Green | `✓` |
| Retry / self-heal triggered | Yellow | `↻` |
| Failure / abort | Red | `✗` |
| Memory recall/write | Magenta | `◆` |
| Final summary line | Bold white | `＝` |

This deliberately echoes the ZAIRE mode-color logic (cyan primary, green success, ember/red for alerts) without reusing ZAIRE's exact hex values — Anvil is a separate open-source identity, not a ZAIRE-branded spinoff.

---

## 3. Verbose Run Output — Layout Spec

Example of what `anvil run research_agent "..."` should look like in `--verbose` mode (structure, not literal final copy):

```
→ Task received: "What caused the 2008 financial crisis?"
◆ Recalling relevant memory... (2 hits)
→ Plan generated (4 steps)
  1. Search for background on 2008 financial crisis
  2. Read top 3 results
  3. Remember key facts
  4. Synthesize cited answer

→ Step 1/4: Search for background on 2008 financial crisis
  … calling tool: web_search(query="2008 financial crisis causes")
  ✓ Step 1 complete (rule check passed)

→ Step 2/4: Read top 3 results
  … calling tool: web_search + fetch (x3)
  ✓ Step 2 complete

→ Step 3/4: Remember key facts
  ◆ memory.remember() x3
  ✓ Step 3 complete

→ Step 4/4: Synthesize cited answer
  ✓ Step 4 complete

＝ Task complete. Trace saved to .anvil/runs/9f3a1c.json
```

On a retry, insert a yellow `↻ Step 2/4 failed quality check — retrying (attempt 2/3)` line before the retried attempt, so failures are visible, not hidden.

---

## 4. Typography & Structure — Docs & README

- **README.md structure (fixed order, do not deviate):**
  1. One-line pitch (the "I built my own orchestration layer" positioning line from the PRD)
  2. 60-second quickstart (exact commands from App Flow §1)
  3. Terminal output GIF or pasted example (from §3 above)
  4. Architecture diagram (ASCII, see §5)
  5. Link to `docs/`
  6. License badge + contribution note
- **Headings:** standard Markdown `#`/`##`/`###`, no custom styling — GitHub-rendered Markdown only, no static site generator required for v1.
- **Code blocks:** always language-tagged (` ```python `, ` ```bash `) for correct GitHub syntax highlighting.
- **Tone:** direct and technical, no marketing language. This is a dev tool read by other devs — avoid the promotional tone that's appropriate for NOXR/ZAIRE marketing copy but wrong here.

---

## 5. Architecture Diagram (ASCII, for README)

This exact diagram (or a visually equivalent generated image) must appear in the README and in `docs/architecture.md`:

```
                     ┌─────────────┐
   Task (string) --> │   Planner   │ <-- Memory (recall)
                     └──────┬──────┘
                            │ Plan (Steps)
                            v
                     ┌─────────────┐
                     │  Executor   │ <-- Tool Registry
                     └──────┬──────┘
                            │ StepResult
                            v
                     ┌──────────────────┐
                     │ QualityEnforcer  │
                     └──────┬───────────┘
                       pass │  fail
                            │     └──────────┐
                            v                v
                        (next Step)   ┌─────────────────┐
                                      │ SelfHealingEngine│
                                      └────────┬─────────┘
                                               │ retry / re-plan
                                               v
                                        (back to Executor
                                         or Planner)
```

---

## 6. Non-Goals for This Brief

- No web dashboard, no GUI mockups — explicitly out of scope (PRD §4).
- No custom docs site (e.g. Docusaurus) required for v1 — plain Markdown in `docs/` rendered by GitHub is sufficient until traction justifies more.
- No logo/brand mark required for launch — a text wordmark ("Anvil") in the README is enough; revisit only if the project gains real traction.
