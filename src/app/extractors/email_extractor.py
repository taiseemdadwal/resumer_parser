"""Regex-based email extractor."""

from __future__ import annotations

import re

from .base import FieldExtractor

_EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


class EmailExtractor(FieldExtractor[str | None]):
    """Extract the first valid-looking email address from text."""

    def extract(self, text: str) -> str | None:
        """Extract the first email match from resume text.

        A simple regex is used to find the first valid-looking email substring.

        Args:
            text: Resume plain text.

        Returns:
            str | None: First matched email address, else ``None``.

        Raises:
            None.
        """

        match = _EMAIL_PATTERN.search(text)
        return match.group(0) if match else None
