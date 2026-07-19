# agent.py
from anvil.agent import AgentRunner
from anvil.config import load_config
from anvil.tools.builtin_fs import read_file, write_file
# import your own tools here too — see docs/first_tool.md

config = load_config("anvil.config.yaml")
MY_TOOLS = [read_file, write_file]

def build_runner(verbose: bool = True) -> AgentRunner:
    return AgentRunner(config=config, tools=MY_TOOLS, verbose=verbose)