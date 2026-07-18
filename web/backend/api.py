"""Trace Dashboard API (Phase 16).

FastAPI backend serving read-only endpoints for runs and memory.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from anvil.memory.store import MemoryStore

app = FastAPI(title="Anvil Trace Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
)

# Directories
ANVIL_DIR = Path(".anvil")
RUNS_DIR = ANVIL_DIR / "runs"
CHROMA_DIR = ANVIL_DIR / "chroma"


@app.get("/api/runs")
def list_runs() -> List[Dict[str, Any]]:
    """List all trace runs in .anvil/runs/."""
    if not RUNS_DIR.exists():
        return []

    summaries = []
    for file_path in RUNS_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                trace = json.load(f)
                summaries.append({
                    "run_id": trace.get("run_id"),
                    "agent_name": trace.get("agent_name"),
                    "task": trace.get("task"),
                    "final_status": trace.get("final_status"),
                    "started_at": trace.get("started_at"),
                })
        except Exception:
            pass  # Skip malformed trace files
            
    # Sort newest first
    summaries.sort(key=lambda x: x.get("started_at", ""), reverse=True)
    return summaries


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> Dict[str, Any]:
    """Get the full JSON trace for a specific run."""
    file_path = RUNS_DIR / f"{run_id}.json"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/agents/{agent_name}/memory")
def get_memory(agent_name: str, collection: str = "semantic", limit: int = 50) -> List[Dict[str, Any]]:
    """Get memory entries for a specific agent."""
    if collection not in ["semantic", "episodic"]:
        raise HTTPException(status_code=400, detail="Invalid collection type")

    try:
        store = MemoryStore(agent_name=agent_name, chroma_path=str(CHROMA_DIR))
        # We can fetch everything or the first N items.
        # ChromaDB doesn't have a simple 'list all' without a query, 
        # but MemoryStore usually exposes something or we can query with empty text.
        # Wait, MemoryStore in anvil/memory/store.py might not have a list() method.
        # Let's peek into Chroma collection directly.
        col = store._client.get_collection(name=f"{agent_name}_{collection}")
        results = col.get(limit=limit)
        
        memories = []
        if results and results["ids"]:
            for i in range(len(results["ids"])):
                memories.append({
                    "id": results["ids"][i],
                    "document": results["documents"][i] if results["documents"] else None,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                })
        
        # Sort newest first based on timestamp in metadata if present
        memories.sort(
            key=lambda x: x.get("metadata", {}).get("timestamp", ""),
            reverse=True
        )
        return memories
    except ValueError as ve:
        # If collection does not exist, chroma raises ValueError
        return []
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

# To serve frontend statically if it exists:
FRONTEND_DIR = Path("web/frontend/dist")
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
