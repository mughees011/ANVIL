# Anvil Architecture

Anvil's execution model is an explicit, synchronous loop. The system does not rely on opaque LLM abstractions; it translates natural language tasks into a graph of strict Pydantic objects that are evaluated sequentially.

## The Core Loop

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

## Components

1. **Planner**: Translates a string task (combined with available tools and recalled semantic memory) into a `Plan` consisting of multiple `Step` objects.
2. **Executor**: Translates a `Step`'s intent into a specific tool call using the Groq LLM client, executes the Python tool, and returns a `StepResult`.
3. **QualityEnforcer**: Evaluates the `StepResult`. First runs a deterministic `rule_check` (e.g. did it crash?), then optionally runs an LLM-graded `rubric_check`.
4. **SelfHealingEngine**: If the quality checks fail, the engine either triggers a same-step retry (for execution crashes) or a partial re-plan (for logic failures), tracking retries up to `max_retries`.
5. **MemoryStore**: Captures the summary of successful steps into `episodic` memory during the run, and can persist facts to `semantic` memory using ChromaDB.
