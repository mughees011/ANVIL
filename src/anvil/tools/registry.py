"""ToolRegistry and the @tool decorator.

- @tool: registers a function with docstring-derived description +
  explicit Pydantic param schema.
- ToolRegistry: collision detection at registration time, fails fast
  (not at call time). to_groq_schema() converts to Groq's native
  function-calling JSON shape.

Full spec: TRD §2 (package structure) and §4 (Groq integration).
Build this in Phase 1 — see Implementation Plan.
"""

# TODO (Phase 1): implement Tool, @tool decorator, ToolRegistry
