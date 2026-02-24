"""LLM-driven skills extractor with deterministic parsing and normalization.

The extractor is intentionally decoupled from any specific vendor SDK by depending on a
minimal ``LLMClient`` protocol. Tests inject a fake client for offline determinism.
"""

from __future__ import annotations

import json
import logging
from json import JSONDecodeError
from typing import Protocol

from .base import FieldExtractor

_MAX_SKILLS = 30
logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """Minimal synchronous LLM client contract."""

    def complete(self, prompt: str) -> str:
        """Generate completion text from a skills extraction prompt.

        Implementations may call local or remote models and return raw text.

        Args:
            prompt: Prompt text provided by the extractor.

        Returns:
            str: Model completion output.

        Raises:
            RuntimeError: Implementations may raise on service/runtime failures.
        """


class SkillsExtractor(FieldExtractor[list[str]]):
    """Extract and normalize skill names from resume text via an injected LLM client."""

    def __init__(self, llm_client: LLMClient) -> None:
        """Initialize skills extractor with an injected LLM client.

        Dependency injection keeps this extractor testable and vendor-agnostic.

        Args:
            llm_client: Concrete implementation of ``LLMClient``.

        Returns:
            None.

        Raises:
            None.
        """

        self._llm_client = llm_client

    def extract(self, text: str) -> list[str]:
        """Extract and normalize skill labels from resume text.

        The response is parsed as JSON array content and normalized for stability.

        Args:
            text: Resume plain text.

        Returns:
            list[str]: Normalized, deduplicated skills list.

        Raises:
            None.
        """

        prompt = _build_prompt(text)
        logger.debug("Skills extraction prompt prepared (chars=%d)", len(prompt))
        response = self._llm_client.complete(prompt)
        logger.debug("Skills strategy response received (chars=%d)", len(response))
        parsed = _parse_response_array(response)
        logger.debug("Parsed %d raw skills from response", len(parsed))
        normalized = _normalize_skills(parsed)
        logger.info("Skills extraction produced %d normalized skills", len(normalized))
        return normalized


def _build_prompt(text: str) -> str:
    """Build a deterministic prompt for skills extraction.

    The prompt explicitly requires array-only JSON output.

    Args:
        text: Resume plain text.

    Returns:
        str: Prompt instructing array-only output.

    Raises:
        None.
    """

    return (
        "Extract skills from the resume text below. "
        "Return ONLY a JSON array of skill strings.\n\n"
        f"Resume text:\n{text}"
    )


def _parse_response_array(response: str) -> list[str]:
    """Parse array-like output from direct or wrapped model responses.

    Both pure-array payloads and responses with surrounding prose are supported.

    Args:
        response: Raw completion text from the LLM client.

    Returns:
        list[str]: Parsed raw skill strings.

    Raises:
        None.
    """

    direct = _parse_json_array(response)
    if direct is not None:
        return direct

    extracted = _extract_first_array_fragment(response)
    if extracted is None:
        return []

    parsed = _parse_json_array(extracted)
    return parsed if parsed is not None else []


def _parse_json_array(value: str) -> list[str] | None:
    """Parse and validate JSON arrays containing string entries.

    Non-list payloads and malformed JSON are treated as non-parsable.

    Args:
        value: Candidate JSON payload.

    Returns:
        list[str] | None: String list when valid, otherwise ``None``.

    Raises:
        None.
    """

    try:
        parsed = json.loads(value)
    except JSONDecodeError:
        return None

    if not isinstance(parsed, list):
        return None

    return [item for item in parsed if isinstance(item, str)]


def _extract_first_array_fragment(value: str) -> str | None:
    """Extract the first balanced JSON-like array fragment.

    This helper scans bracket depth to isolate the first valid array segment.

    Args:
        value: Raw text potentially containing a JSON array.

    Returns:
        str | None: Extracted array fragment or ``None`` if not found.

    Raises:
        None.
    """

    start = value.find("[")
    if start == -1:
        return None

    depth = 0
    for index in range(start, len(value)):
        char = value[index]
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return value[start : index + 1]

    return None


def _normalize_skills(skills: list[str]) -> list[str]:
    """Normalize skill labels for stable output shape.

    Normalization strips whitespace, deduplicates case-insensitively, and caps size.

    Args:
        skills: Raw parsed skill labels.

    Returns:
        list[str]: Trimmed, deduplicated, capped skill list.

    Raises:
        None.
    """

    normalized: list[str] = []
    seen: set[str] = set()

    for skill in skills:
        cleaned = skill.strip()
        if not cleaned:
            continue

        key = cleaned.lower()
        if key in seen:
            continue

        normalized.append(cleaned)
        seen.add(key)

        if len(normalized) >= _MAX_SKILLS:
            break

    return normalized
