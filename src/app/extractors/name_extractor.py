"""Heuristic name extractor.

The strategy favors high-signal lines near the top of resume text and filters out common
section headings and non-name patterns.
"""

from __future__ import annotations

import re

from .base import FieldExtractor

_MAX_LINES = 10
_WORD_PATTERN = re.compile(r"^[A-Za-z][A-Za-z'\\-]*$")
_HEADING_TERMS = {
    "resume",
    "curriculum vitae",
    "summary",
    "experience",
    "education",
    "skills",
    "projects",
}


class NameExtractor(FieldExtractor[str | None]):
    """Extract candidate name from the first lines of resume text."""

    def extract(self, text: str) -> str | None:
        """Extract the best name candidate from top resume lines.

        The strategy applies lightweight normalization, filtering, and scoring heuristics.

        Args:
            text: Resume plain text.

        Returns:
            str | None: Best detected name candidate or ``None``.

        Raises:
            None.
        """

        candidates: list[tuple[tuple[int, int], str]] = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        for index, raw_line in enumerate(lines[:_MAX_LINES]):
            candidate = _normalize_candidate(raw_line)
            if _is_name_candidate(candidate):
                candidates.append((_score_candidate(candidate, index), candidate))

        if not candidates:
            return None

        candidates.sort(reverse=True)
        return candidates[0][1]


def _normalize_candidate(line: str) -> str:
    """Normalize a single line candidate before heuristic checks.

    Heading markers and optional ``Name:`` prefixes are removed.

    Args:
        line: Raw line candidate.

    Returns:
        str: Normalized line value.

    Raises:
        None.
    """

    cleaned = line.strip().lstrip("-•* ")
    if cleaned.lower().startswith("name:"):
        _, value = cleaned.split(":", maxsplit=1)
        return value.strip()
    return cleaned


def _is_heading(line: str) -> bool:
    """Check whether a line is likely a section heading.

    Heading detection filters noisy lines like ``Summary`` or ``Experience``.

    Args:
        line: Candidate line.

    Returns:
        bool: ``True`` if heading-like terms are detected.

    Raises:
        None.
    """

    lowered = line.lower()
    return any(term in lowered for term in _HEADING_TERMS)


def _is_name_candidate(line: str) -> bool:
    """Evaluate whether a normalized line satisfies name heuristics.

    The candidate must look alphabetic, short, and free of email/digit patterns.

    Args:
        line: Normalized candidate line.

    Returns:
        bool: ``True`` when the line matches expected name constraints.

    Raises:
        None.
    """

    if "@" in line or any(character.isdigit() for character in line) or _is_heading(line):
        return False

    words = [word for word in line.split() if word]
    if not 2 <= len(words) <= 4:
        return False

    return all(_WORD_PATTERN.fullmatch(word) for word in words)


def _score_candidate(line: str, index: int) -> tuple[int, int]:
    """Score candidate names for deterministic ranking.

    Higher title-case score and earlier line position are preferred.

    Args:
        line: Normalized candidate line.
        index: Original line index in the scanned text window.

    Returns:
        tuple[int, int]: Composite score tuple used for sorting.

    Raises:
        None.
    """

    words = line.split()
    title_case = sum(word[0].isupper() for word in words)
    return (title_case, -index)
