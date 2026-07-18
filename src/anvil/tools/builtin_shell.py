"""Built-in shell tool: run_shell_command (sandboxed, opt-in).

Disabled by default. Requires AgentConfig.allow_shell_tool=True AND
AgentConfig.shell_jail_dir set — refuses to run otherwise, no silent
fallback to cwd.

subprocess.run(cmd, cwd=jail_dir, timeout=..., capture_output=True, shell=False)
shell=False, args as a list — never a raw string. Never a full OS sandbox
in v1 (no Docker/gVisor) — documented limitation, not hidden.

Exact resolved design: TRD §8.
"""

# TODO (Phase 1): implement run_shell_command with sandboxing per TRD §8
