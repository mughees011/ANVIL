"""Built-in filesystem tools: read_file, write_file.

Opt-in like all built-ins — agent author must explicitly register these.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from anvil.tools.registry import Tool, tool


# ── Parameter schemas ──────────────────────────────────────────────────────────

class ReadFileParams(BaseModel):
    path: str


class WriteFileParams(BaseModel):
    path: str
    content: str
    create_dirs: bool = True


# ── Tool implementations ───────────────────────────────────────────────────────

@tool(params_schema=ReadFileParams)
def read_file(path: str) -> str:
    """Read the contents of a file at the given path and return them as a string."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return p.read_text(encoding="utf-8")


@tool(params_schema=WriteFileParams)
def write_file(path: str, content: str, create_dirs: bool = True) -> str:
    """Write content to a file at the given path, creating parent directories if needed."""
    p = Path(path)
    if create_dirs:
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written {len(content)} bytes to {path}"


# ── Convenience list for agent authors ────────────────────────────────────────

BUILTIN_FS_TOOLS: list[Tool] = [read_file, write_file]  # type: ignore[list-item]
