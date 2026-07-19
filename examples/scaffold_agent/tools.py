"""Tools for the scaffold_agent."""

from anvil.tools.builtin_fs import BUILTIN_FS_TOOLS
from anvil.tools.builtin_shell import run_shell_command
from anvil.tools.registry import Tool

# Combine filesystem tools with the sandboxed shell tool
MY_TOOLS: list[Tool] = [*BUILTIN_FS_TOOLS, run_shell_command]  # type: ignore[list-item]
