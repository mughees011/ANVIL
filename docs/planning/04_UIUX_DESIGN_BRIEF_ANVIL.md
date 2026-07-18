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

## 7. Trace Dashboard Visual Design (Post-Core, Phase 16)

Resolves PRD §7.8. This section governs the React dashboard specifically — it's a real GUI, so it gets a real design spec, same rigor as the terminal spec above, not left ad hoc.

### 7.1 Palette
Dark-glass base, consistent with the prototype already built — formalized as design tokens rather than eyeballed per component:

| Token | Hex (approx, adjust in implementation) | Usage |
|---|---|---|
| `--bg-base` | `#0A0B0E` | Page background |
| `--bg-panel` | `#12141A` (semi-transparent, glass effect) | Cards, sidebar |
| `--accent-cyan` | `#22D3EE` | Primary actions, active nav item, info states |
| `--accent-purple` | `#A855F7` | Logo gradient, memory-related UI (echoes the terminal's magenta memory color) |
| `--accent-green` | `#22C55E` | Success states |
| `--accent-amber` | `#F59E0B` | Self-heal / retry states |
| `--text-primary` | `#F1F5F9` | Headings, primary text |
| `--text-muted` | `#64748B` | Labels, secondary text |

This is a distinct palette from ZAIRE's exact hex values (per the original design principle in §1 — separate open-source identity), but intentionally similar in spirit: dark, glass, cyan-forward.

### 7.2 Layout Pattern
Fixed left sidebar (logo + nav: Overview, Runs, Plan & Trace, Memory, Architecture) + main content area, matching the structure already built. Stat cards use large colored numerals with a muted label beneath — keep this pattern for any new stat additions rather than inventing a new card style.

### 7.3 Status Color Reuse
The dashboard's status indicators must reuse the exact color-to-meaning mapping from §2 (terminal vocabulary), not a separate scheme — e.g. a "SUCCESS" badge is `--accent-green`, a step that triggered self-healing shows `--accent-amber`, consistent with the CLI's `↻` yellow retry line. One user, two surfaces, one learned color vocabulary.

### 7.4 Typography
Sans-serif throughout (the prototype's font is fine — e.g. Inter or system-ui stack), with monospace (`ui-monospace` / `JetBrains Mono`) reserved specifically for: run IDs, file paths, JSON snippets, and trace file names — anything that's literally code or an identifier, mirroring how the terminal output distinguishes prose from data.

---

## 8. Non-Goals for This Brief

- The web dashboard (§7) is now in scope as a post-core companion tool — this line originally excluded it entirely; superseded by PRD §7.8 and TRD §13. What remains out of scope: any *hosted/multi-user* GUI, and any mockup work beyond §7's token-level spec (no per-screen Figma-style mockups produced here — §7's tokens + the layout pattern already built are considered sufficient direction).
- No custom docs site (e.g. Docusaurus) required for v1 — plain Markdown in `docs/` rendered by GitHub is sufficient until traction justifies more.
- No logo/brand mark required for launch beyond the dashboard's existing wordmark + gradient icon (already built) — a text wordmark ("Anvil") in the README is enough for the GitHub-facing side; revisit only if the project gains real traction.
