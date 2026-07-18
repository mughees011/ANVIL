"""ToolRegistry and the @tool decorator.

- @tool: wraps a Python function, attaches a Tool descriptor with
  docstring-derived description + explicit Pydantic param schema.
- ToolRegistry: collision detection at registration time (fails fast,
  not at call time). to_groq_schema() converts to Groq's native
  function-calling JSON shape.

Full spec: TRD §2 (package structure) and §4 (Groq integration).
"""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Type

from pydantic import BaseModel


@dataclass
class Tool:
    """Descriptor for a registered tool."""

    name: str
    description: str
    fn: Callable[..., Any]
    params_schema: Type[BaseModel]

    def to_groq_schema(self) -> dict:
        """Return this tool as a Groq-compatible tool object."""
        raw_schema = self.params_schema.model_json_schema()
        # Remove Pydantic's title at the top level — Groq doesn't need it.
        raw_schema.pop("title", None)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": raw_schema,
            },
        }

    def execute(self, **kwargs: Any) -> Any:
        """Validate args against the schema then call the underlying function."""
        validated = self.params_schema(**kwargs)
        return self.fn(**validated.model_dump())


def tool(
    params_schema: Type[BaseModel],
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Callable:
    """Decorator that wraps a function into a Tool descriptor.

    Usage::

        class SearchParams(BaseModel):
            query: str

        @tool(params_schema=SearchParams)
        def web_search(query: str) -> str:
            \"\"\"Search the web for a query.\"\"\"
            ...

    Args:
        params_schema: Pydantic model describing the tool's parameters.
        name: Override the tool name (defaults to the function's __name__).
        description: Override the description (defaults to the function's docstring).
    """

    def decorator(fn: Callable) -> Tool:
        tool_name = name or fn.__name__
        tool_description = description or (inspect.getdoc(fn) or "")
        return Tool(
            name=tool_name,
            description=tool_description,
            fn=fn,
            params_schema=params_schema,
        )

    return decorator


class ToolRegistry:
    """Registry that holds all tools available to an agent.

    Collision detection happens at registration time — duplicate tool
    names raise immediately rather than silently overwriting.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, t: Tool) -> None:
        """Register a Tool. Raises ValueError on name collision."""
        if t.name in self._tools:
            raise ValueError(
                f"Tool name collision: '{t.name}' is already registered. "
                "Each tool must have a unique name within an agent."
            )
        self._tools[t.name] = t

    def get(self, name: str) -> Optional[Tool]:
        """Return the Tool with the given name, or None if not found."""
        return self._tools.get(name)

    def all(self) -> list[Tool]:
        """Return all registered tools."""
        return list(self._tools.values())

    def names(self) -> list[str]:
        """Return all registered tool names."""
        return list(self._tools.keys())

    def to_groq_schema(self) -> list[dict]:
        """Return all tools formatted as Groq's `tools` parameter list."""
        return [t.to_groq_schema() for t in self._tools.values()]

    def __len__(self) -> int:
        return len(self._tools)

    def __repr__(self) -> str:  # pragma: no cover
        return f"ToolRegistry(tools={self.names()})"
