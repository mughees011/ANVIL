# Writing an Agent

An agent in Anvil is an instance of `AgentRunner` configured with a specific set of tools and a model configuration.

## 1. Setup the Config
Create a file named `anvil.config.yaml` in your agent's directory:

```yaml
name: my_first_agent
planner_model: "llama-3.3-70b-versatile"
executor_model: "llama-3.3-70b-versatile"
max_retries: 3
memory_top_k: 5
halt_on_failure: true
allow_shell_tool: false
```

## 2. Write the Runner
Create `agent.py`:

```python
from pathlib import Path
from anvil.agent import AgentRunner
from anvil.config import load_config
from my_agent.tools import MY_TOOLS

def main():
    # 1. Load the configuration
    config_path = Path(__file__).parent / "anvil.config.yaml"
    config = load_config(config_path)

    # 2. Instantiate the runner
    runner = AgentRunner(
        config=config, 
        tools=MY_TOOLS, 
        verbose=True
    )

    # 3. Execute a task
    result = runner.run("Research the history of Python")
    
    print(f"Status: {result.status}")
    print(f"Trace saved to: {result.trace_path}")

if __name__ == "__main__":
    main()
```

## 3. Execution
You can execute your agent via the CLI to automatically capture the trace and output:
```bash
anvil run my_first_agent "Research the history of Python"
```
