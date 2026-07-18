"""MemoryStore — wraps ChromaDB PersistentClient(path=".anvil/chroma/").

Two collections per agent: {agent_name}_episodic, {agent_name}_semantic
(naming enforced here, not configurable — see Backend Schema §2 for
exact field-level schema of each).

remember(text, metadata, collection="episodic") / recall(query, k, collection)

Episodic clears at start of next Task unless explicitly promoted to
semantic. Embedding fn: ChromaDB's bundled default (all-MiniLM-L6-v2),
no external API call — keeps this genuinely local-first.

Build this in Phase 2 — see Implementation Plan. Test with tmp_path,
never the real .anvil/chroma/.
"""

# TODO (Phase 2): implement MemoryStore
