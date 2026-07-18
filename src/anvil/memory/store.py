"""MemoryStore — wraps ChromaDB PersistentClient(path=".anvil/chroma/").

Two collections per agent: {agent_name}_episodic, {agent_name}_semantic.
See Backend Schema §2 for the exact field-level schema of each.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

import chromadb
from chromadb.config import Settings
from pydantic import BaseModel


class MemoryHit(BaseModel):
    """A single result from a memory recall query."""

    id: str
    document: str
    metadata: dict
    distance: float


class MemoryStore:
    """Local ChromaDB-backed memory with episodic and semantic collections.

    Args:
        agent_name: Used as the collection name prefix.
        chroma_path: On-disk path for ChromaDB storage (default: .anvil/chroma/).
    """

    EPISODIC = "episodic"
    SEMANTIC = "semantic"

    def __init__(self, agent_name: str, chroma_path: str | Path = ".anvil/chroma/") -> None:
        self.agent_name = agent_name
        self._client = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=Settings(anonymized_telemetry=False),
        )
        # Get-or-create both collections up front.
        self._episodic = self._client.get_or_create_collection(
            name=f"{agent_name}_episodic"
        )
        self._semantic = self._client.get_or_create_collection(
            name=f"{agent_name}_semantic"
        )

    def _collection(self, which: Literal["episodic", "semantic"]):
        return self._episodic if which == self.EPISODIC else self._semantic

    def remember(
        self,
        text: str,
        metadata: Optional[dict] = None,
        collection: Literal["episodic", "semantic"] = "episodic",
        run_id: Optional[str] = None,
        step_id: Optional[str] = None,
    ) -> str:
        """Store a text fragment in the given collection.

        Args:
            text: The content to remember.
            metadata: Optional extra metadata merged with the standard fields.
            collection: "episodic" (default) or "semantic".
            run_id: The current run ID (attached as metadata).
            step_id: The current step ID (attached as metadata).

        Returns:
            The UUID of the stored document.
        """
        doc_id = str(uuid.uuid4())
        base_meta: dict = {
            "memory_type": collection,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if run_id:
            base_meta["run_id"] = run_id
        if step_id:
            base_meta["step_id"] = step_id
        if collection == self.SEMANTIC and run_id:
            base_meta["promoted_from_run_id"] = run_id
        if metadata:
            base_meta.update(metadata)

        self._collection(collection).add(
            ids=[doc_id],
            documents=[text],
            metadatas=[base_meta],
        )
        return doc_id

    def recall(
        self,
        query: str,
        k: int = 5,
        collection: Literal["episodic", "semantic", "both"] = "both",
    ) -> list[MemoryHit]:
        """Retrieve the top-k most relevant memories via similarity search.

        Args:
            query: The text to search for.
            k: Number of results to return.
            collection: Which collection(s) to search.

        Returns:
            List of MemoryHit objects sorted by relevance (closest first).
        """
        hits: list[MemoryHit] = []

        def _query(coll, n: int) -> list[MemoryHit]:
            if coll.count() == 0:
                return []
            results = coll.query(
                query_texts=[query],
                n_results=min(n, coll.count()),
            )
            out = []
            for doc, meta, dist, doc_id in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
                results["ids"][0],
            ):
                out.append(MemoryHit(id=doc_id, document=doc, metadata=meta, distance=dist))
            return out

        if collection in (self.EPISODIC, "both"):
            hits.extend(_query(self._episodic, k))
        if collection in (self.SEMANTIC, "both"):
            hits.extend(_query(self._semantic, k))

        # Sort by distance (lower = more similar) and cap at k.
        hits.sort(key=lambda h: h.distance)
        return hits[:k]

    def clear_episodic(self) -> None:
        """Delete all episodic memories for this agent (called at end of run)."""
        ids = self._episodic.get()["ids"]
        if ids:
            self._episodic.delete(ids=ids)

    def promote_to_semantic(self, doc_id: str) -> bool:
        """Copy an episodic entry into semantic memory.

        Returns True on success, False if the doc_id was not found.
        """
        result = self._episodic.get(ids=[doc_id])
        if not result["ids"]:
            return False
        doc = result["documents"][0]
        meta = dict(result["metadatas"][0])
        meta["memory_type"] = "semantic"
        meta["promoted_from_run_id"] = meta.get("run_id", "")
        self._semantic.add(ids=[str(uuid.uuid4())], documents=[doc], metadatas=[meta])
        return True
