# Memory Guide

Anvil uses ChromaDB as its persistent, local-first vector store for memory. It divides memory into two collections to separate short-term context from long-term knowledge.

## Episodic Memory

Episodic memory tracks what happened during the current run.
- **When is it written?** Automatically. `AgentRunner` records a summary of every successful `StepResult` to the episodic collection.
- **When is it cleared?** Automatically. `AgentRunner` flushes the episodic collection at the end of the run.
- **Usage**: Allows the Planner to maintain context within a single complex task without filling up the prompt window infinitely.

## Semantic Memory

Semantic memory tracks persistent facts, user preferences, and cross-run knowledge.
- **When is it written?** Manually. The agent logic or tools must explicitly call `memory.remember(document, collection="semantic")`.
- **When is it cleared?** Never automatically.
- **Usage**: Allows the agent to learn facts over time. The Planner automatically queries semantic memory at the beginning of a run to inject relevant context into its plan generation prompt.

## Under the Hood

The `MemoryStore` initializes a `chromadb.PersistentClient` in `.anvil/chroma/`. It uses a fast local embedding model to encode documents, meaning zero network calls are made for memory storage or retrieval.
