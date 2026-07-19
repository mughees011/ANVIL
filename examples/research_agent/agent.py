"""Research Agent — proves Anvil's memory + planning in a non-code domain.

Flow (App Flow §5): search topic -> read top results -> remember key
facts -> synthesize cited answer.

Build in Phase 12 — after the full core loop (Phases 1-11) is done.
"""

from pathlib import Path
from anvil.agent import AgentRunner
from anvil.config import load_config

# Import our custom tools
from examples.research_agent.tools import MY_TOOLS

def main():
    # Load configuration
    config_path = Path(__file__).parent / "anvil.config.yaml"
    config = load_config(config_path)

    # Initialize the runner
    runner = AgentRunner(config=config, tools=MY_TOOLS, verbose=True)

    # Execute the research task
    task = "What caused the 2008 financial crisis?"
    result = runner.run(task)
    
    print(f"\nFinal Status: {result.status}")
    print(f"Trace saved to: {result.trace_path}")

if __name__ == "__main__":
    main()
