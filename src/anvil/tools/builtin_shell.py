"""Built-in shell tool: run_shell_command (sandboxed, opt-in).

Disabled by default. Requires AgentConfig.allow_shell_tool=True AND
AgentConfig.shell_jail_dir set — refuses to run otherwise, no silent
fallback to cwd. See TRD §8 for the resolved design.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from anvil.tools.registry import tool


class ShellCommandParams(BaseModel):
    cmd: list[str]
    """Command as a list of strings — never a raw string (prevents injection)."""
    timeout: Optional[int] = None
    """Override the configured timeout for this call. If None, uses config default."""


@tool(params_schema=ShellCommandParams)
def run_shell_command(cmd: list[str], timeout: Optional[int] = None) -> dict:
    """Run a shell command in a sandboxed jail directory. Returns stdout, stderr, returncode.

    This tool is DISABLED by default. The AgentConfig must explicitly set
    allow_shell_tool=true AND shell_jail_dir to use it.

    Note: This function is a template. The actual jail_dir and timeout
    are injected by the Executor at call time using AgentConfig values,
    because the @tool decorator cannot access the runtime config.
    """
    raise PermissionError(
        "run_shell_command must be invoked via the Executor with shell config injected. "
        "Do not call it directly without going through AgentRunner."
    )


def _execute_shell_command(
    cmd: list[str],
    jail_dir: Path,
    timeout: int,
) -> dict:
    """Internal: actually run the command.

    Called by Executor after verifying allow_shell_tool=True and jail_dir is set.
    Separated from the @tool so tests can call this directly.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=str(jail_dir),
            timeout=timeout,
            capture_output=True,
            shell=False,  # Never shell=True — prevents injection
            text=True,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f"Command timed out after {timeout}s: {' '.join(cmd)}"
        ) from exc
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Command not found: {cmd[0]}"
        ) from exc
