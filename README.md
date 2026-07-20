# Anvil

> A local-first Python framework for building AI agents with planning, memory, tool calling, and self-healing. I built my own orchestration layer so you don't have to.

## 60-Second Quickstart

```bash
# 1. Install the framework
pip install -e .

# 2. Setup your API key
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY

# 3. Scaffold a new agent
anvil init my_agent
# This creates my_agent/agent.py, my_agent/tools.py, and my_agent/anvil.config.yaml

# 4. Write your tools
# Edit my_agent/tools.py to add Python functions decorated with @tool

# 5. Configure your agent
# Edit my_agent/agent.py to import your tools and configure AgentRunner

# 6. Run your agent
anvil run my_agent "some task in plain English"

# 7. View the trace of a past run
anvil trace <run_id>
```

## Terminal Output Example

Running `anvil run research_agent "What caused the 2008 financial crisis?" --verbose`:

```
→ Task received: "What caused the 2008 financial crisis?"
◆ Recalling relevant memory... (2 hits)
→ Plan generated (4 steps)
  1. Search for background on 2008 financial crisis
  2. Read top 3 results
  3. Remember key facts
  4. Synthesize cited answer

→ Step 1/4: Search for background on 2008 financial crisis
  … calling tool: wikipedia_search(query="2008 financial crisis causes")
  ✓ Step 1 complete (rule check passed)

→ Step 2/4: Read top 3 results
  … calling tool: wikipedia_search (x3)
  ✓ Step 2 complete

→ Step 3/4: Remember key facts
  ◆ memory.remember() x3
  ✓ Step 3 complete

→ Step 4/4: Synthesize cited answer
  ✓ Step 4 complete

＝ Task complete. Trace saved to .anvil/runs/9f3a1c.json
```

## Architecture

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

## Documentation

- [Architecture Guide](docs/architecture.md)
- [Memory Guide](docs/memory.md)
- [Writing a Tool](docs/writing_a_tool.md)
- [Writing an Agent](docs/writing_an_agent.md)
- [FAQ](docs/faq.md)

## License and Contributing

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Anvil is released under the MIT License. Contributions, pull requests, and bug reports are welcome.
