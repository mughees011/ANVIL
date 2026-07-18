"""GroqClient — thin wrapper around the groq SDK.

chat() and chat_with_tools() with retry/backoff on transient errors
(429, 5xx — exponential backoff, max 3 attempts, base delay 1s).
This is transport-error retry, distinct from SelfHealingEngine.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from groq import Groq, APIStatusError, APIConnectionError


_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 3
_BASE_DELAY_S = 1.0


class GroqClient:
    """Thin, retry-aware wrapper around the Groq SDK client.

    Args:
        api_key: Groq API key. If omitted, the GROQ_API_KEY env var is used
                 by the underlying SDK (which also calls dotenv internally).
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        kwargs: dict[str, Any] = {}
        if api_key:
            kwargs["api_key"] = api_key
        self._client = Groq(**kwargs)

    # ── Public interface ───────────────────────────────────────────────────────

    def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        """Send a plain chat completion request and return the text response.

        Args:
            messages: List of chat messages in OpenAI format.
            model: Groq model slug (e.g. "llama-3.3-70b-versatile").
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.

        Returns:
            The assistant's text response.

        Raises:
            APIStatusError: On non-retryable HTTP errors (e.g. 401 bad key).
            RuntimeError: If all retry attempts are exhausted.
        """
        response = self._call_with_retry(
            self._client.chat.completions.create,
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> dict:
        """Send a tool-calling chat request and return the full message object.

        Args:
            messages: List of chat messages in OpenAI format.
            tools: Groq-formatted tools list (from ToolRegistry.to_groq_schema()).
            model: Groq model slug.
            temperature: Sampling temperature (default 0 for determinism).
            max_tokens: Maximum tokens in the response.

        Returns:
            The raw Groq message object (as a dict) which may contain
            `content` and/or `tool_calls`.

        Raises:
            APIStatusError: On non-retryable HTTP errors.
            RuntimeError: If all retry attempts are exhausted.
        """
        response = self._call_with_retry(
            self._client.chat.completions.create,
            messages=messages,
            tools=tools,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message  # type: ignore[return-value]

    # ── Internal retry logic ───────────────────────────────────────────────────

    def _call_with_retry(self, fn, **kwargs) -> Any:
        """Call `fn(**kwargs)` with exponential backoff on transient errors.

        Retries up to _MAX_ATTEMPTS times on 429/5xx status codes.
        Non-retryable errors (e.g. 401) are re-raised immediately.
        """
        last_exc: Optional[Exception] = None
        for attempt in range(_MAX_ATTEMPTS):
            try:
                return fn(**kwargs)
            except APIStatusError as exc:
                if exc.status_code not in _RETRYABLE_STATUS_CODES:
                    raise  # 401 bad key, 400 bad request, etc. — don't retry
                last_exc = exc
                delay = _BASE_DELAY_S * (2 ** attempt)
                time.sleep(delay)
            except APIConnectionError as exc:
                last_exc = exc
                delay = _BASE_DELAY_S * (2 ** attempt)
                time.sleep(delay)

        raise RuntimeError(
            f"Groq API call failed after {_MAX_ATTEMPTS} attempts. "
            f"Last error: {last_exc}"
        ) from last_exc
