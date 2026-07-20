# Writing a Tool

A tool in Anvil is simply a Python function decorated with `@tool`.

## 1. Define the Parameters
First, create a Pydantic `BaseModel` that strictly defines the inputs to your tool. Anvil uses this schema to tell the LLM exactly how to call your tool.

```python
from pydantic import BaseModel

class WebSearchParams(BaseModel):
    query: str
```

## 2. Write the Tool
Next, write your Python function and decorate it. 

```python
from anvil.tools.registry import tool

@tool(params_schema=WebSearchParams)
def web_search(query: str) -> str:
    """Search the web for the given query and return a summary."""
    # Your logic here
    return "Results for " + query
```

**Important Rules:**
1. The docstring of your function is critical. The LLM reads it to understand *when* and *why* to use your tool.
2. The function must return a string or a JSON-serializable dictionary.
3. If your tool fails, it should raise an exception. The `Executor` will catch it and trigger Anvil's Self-Healing loop automatically.
