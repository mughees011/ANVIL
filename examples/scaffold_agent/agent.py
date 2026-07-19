"""Scaffold Agent — small, generalized version of ZAIRE's Engineer Mode.

Deliberately scoped smaller than ZAIRE's actual Engineer Mode (PRD §7.6).
Flow (App Flow §5): plan file structure -> write files -> quality check
(files exist + syntactically valid).

Build in Phase 13 — after Research Agent (Phase 12).
"""

from pathlib import Path
from anvil.agent import AgentRunner
from anvil.config import load_config

# Import our custom tools
from examples.scaffold_agent.tools import MY_TOOLS

def main():
    # Load configuration
    config_path = Path(__file__).parent / "anvil.config.yaml"
    config = load_config(config_path)

    # Initialize the runner
    runner = AgentRunner(config=config, tools=MY_TOOLS, verbose=True)

    # Ensure jail dir exists
    jail_dir = Path(config.shell_jail_dir)
    jail_dir.mkdir(parents=True, exist_ok=True)

    # Execute the scaffolding task
    task = "Build a Flask API with a /health endpoint"
    result = runner.run(task)
    
    print(f"\nFinal Status: {result.status}")
    print(f"Trace saved to: {result.trace_path}")

if __name__ == "__main__":
    main()
