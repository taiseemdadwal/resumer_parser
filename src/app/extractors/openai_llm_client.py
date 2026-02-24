"""Optional OpenAI-backed implementation of the ``LLMClient`` protocol.

This adapter is intentionally isolated from the core extractor logic so the project can run
without OpenAI dependencies unless explicitly enabled by the caller.
"""

from __future__ import annotations

import importlib
import logging
import os
from typing import Any

from app.extractors.skills_extractor import LLMClient

logger = logging.getLogger(__name__)


class OpenAILLMClient(LLMClient):
    """LLM client adapter that calls OpenAI Chat Completions.

    The adapter validates API credentials at initialization and raises clear runtime errors
    for missing dependencies or API execution failures.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        timeout_seconds: float = 30,
    ) -> None:
        """Initialize OpenAI client wrapper.

        The SDK import is resolved lazily to keep base installs lightweight.

        Args:
            model: OpenAI model name used for chat completion.
            api_key: API key override. Defaults to ``OPENAI_API_KEY``.
            timeout_seconds: Request timeout passed to OpenAI client.

        Returns:
            None.

        Raises:
            ValueError: If no API key is available.
            RuntimeError: If OpenAI SDK is not installed.
        """

        resolved_key = api_key or os.getenv("OPENAI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "Missing OpenAI API key. Set OPENAI_API_KEY or pass api_key."
            )

        self._model = model
        logger.debug("Initializing OpenAILLMClient with model '%s'", model)

        try:
            openai_module = importlib.import_module("openai")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "OpenAI SDK is not installed. Install with: pip install -e '.[llm]'"
            ) from exc

        openai_constructor = getattr(openai_module, "OpenAI")
        self._client: Any = openai_constructor(api_key=resolved_key, timeout=timeout_seconds)

    def complete(self, prompt: str) -> str:
        """Execute one chat completion call and return response text.

        The request uses deterministic settings and enforces JSON-array-only behavior.

        Args:
            prompt: Prompt instructing the model to output skills JSON.

        Returns:
            str: Raw completion text returned by the OpenAI API.

        Raises:
            RuntimeError: If the API call fails or response content is missing.
        """

        logger.debug(
            "Sending OpenAI completion request (model=%s, prompt_chars=%d)",
            self._model,
            len(prompt),
        )
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return only a JSON array of skill strings. "
                            "No prose, markdown, or extra text."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
        except Exception as exc:  # pragma: no cover - depends on external SDK/runtime
            raise RuntimeError(
                f"OpenAI completion failed for model '{self._model}': {exc}"
            ) from exc

        text = _extract_text(response)
        if text is None:
            raise RuntimeError(
                f"OpenAI response for model '{self._model}' had no text content"
            )

        logger.debug("Received OpenAI completion text (chars=%d)", len(text))
        return text


def _extract_text(response: Any) -> str | None:
    """Extract text content from an OpenAI chat completion response object.

    The helper returns ``None`` when expected message content is absent.

    Args:
        response: SDK response object.

    Returns:
        str | None: Message content when available, otherwise ``None``.

    Raises:
        None.
    """

    choices = getattr(response, "choices", None)
    if not choices:
        return None

    first_choice = choices[0]
    message = getattr(first_choice, "message", None)
    if message is None:
        return None

    content = getattr(message, "content", None)
    return content if isinstance(content, str) else None
