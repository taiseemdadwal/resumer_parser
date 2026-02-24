"""Domain models for structured resume extraction output.

This module intentionally defines a small, stable data contract that remains independent
from parser and extractor implementation details. The `ResumeData` dataclass is the single
output object produced by the framework orchestration layer.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class ResumeData:
    """Structured resume fields extracted from unstructured document text.

    Attributes:
        name: Candidate full name when identified, otherwise ``None``.
        email: First valid email address found, otherwise ``None``.
        skills: Normalized list of extracted skill labels.

    The class is frozen to make extracted results immutable after creation. This keeps
    downstream handling predictable and avoids accidental mutation.
    """

    name: str | None = None
    email: str | None = None
    skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, str | None | list[str]]:
        """Convert the dataclass payload into a plain dictionary.

        This helper returns a serialization-friendly mapping for CLI and tests.

        Args:
            None.

        Returns:
            dict[str, str | None | list[str]]: Serializable representation of the resume data.

        Raises:
            None.
        """

        return asdict(self)
