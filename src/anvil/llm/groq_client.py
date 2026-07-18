"""GroqClient — thin wrapper around the groq SDK.

chat() and chat_with_tools() with retry/backoff on transient errors
(429, 5xx — exponential backoff, max 3 attempts, base delay 1s).
This is transport-error retry, distinct from SelfHealingEngine
(logic-error retry) — see TRD §4 and §7 for the distinction.

API key resolution order: TRD §4 / Backend Schema §5.
Build this in Phase 3 — see Implementation Plan.
"""

# TODO (Phase 3): implement GroqClient

# --- tools/ ---
touch __init__.py 2>/dev/null
cat > tools/__init__.py << 'EOF'
