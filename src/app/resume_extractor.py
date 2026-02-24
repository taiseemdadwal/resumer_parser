"""Coordinator for extracting structured fields from plain resume text."""

from __future__ import annotations

import logging
from collections.abc import Mapping

from app.domain.models import ResumeData
from app.extractors.base import ExtractionError, FieldExtractor

_REQUIRED_KEYS = {"name", "email", "skills"}
logger = logging.getLogger(__name__)


class ResumeExtractor:
    """Orchestrate field-level extraction using dependency-injected extractors.

    The coordinator expects a dictionary of field extractor instances keyed by field name.
    This keeps field strategy selection outside orchestration logic and allows easy
    substitution in tests or runtime composition.
    """

    def __init__(self, field_extractors: Mapping[str, FieldExtractor[object]]) -> None:
        """Initialize coordinator with required field extractor instances.

        The provided mapping must include extractor objects for all required fields.

        Args:
            field_extractors: Mapping with required keys ``name``, ``email``, ``skills``.

        Returns:
            None.

        Raises:
            ValueError: If any required extractor key is missing.
        """

        missing = sorted(_REQUIRED_KEYS.difference(field_extractors))
        if missing:
            raise ValueError(f"Missing required field extractors: {', '.join(missing)}")

        # Store an internal mutable copy while keeping the constructor contract flexible.
        self._field_extractors = dict(field_extractors)

    def extract(self, text: str) -> ResumeData:
        """Extract all required fields from plain text and return ``ResumeData``.

        Each field extractor runs independently and results are type-validated.

        Args:
            text: Resume plain text.

        Returns:
            ResumeData: Structured extraction output.

        Raises:
            ExtractionError: If any extractor raises unexpectedly.
        """

        logger.debug("Starting coordinated extraction for %d characters of text", len(text))
        name = self._extract_field("name", text)
        email = self._extract_field("email", text)
        skills = self._extract_field("skills", text)

        if not isinstance(name, (str, type(None))):
            raise ExtractionError("Name extractor returned invalid type")
        if not isinstance(email, (str, type(None))):
            raise ExtractionError("Email extractor returned invalid type")
        if not isinstance(skills, list) or not all(isinstance(skill, str) for skill in skills):
            raise ExtractionError("Skills extractor returned invalid type")

        logger.info(
            "Extraction completed for fields: name=%s email=%s skills_count=%d",
            bool(name),
            bool(email),
            len(skills),
        )
        return ResumeData(name=name, email=email, skills=skills)

    def _extract_field(self, field_name: str, text: str) -> object:
        """Extract a single field and wrap unexpected errors with field context.

        This helper centralizes exception wrapping to provide consistent diagnostics.

        Args:
            field_name: Dictionary key for the configured field extractor.
            text: Plain resume text.

        Returns:
            Extracted field value as a generic object.

        Raises:
            ExtractionError: If the target extractor raises unexpectedly.
        """

        try:
            logger.debug("Extracting field '%s'", field_name)
            return self._field_extractors[field_name].extract(text)
        except Exception as exc:  # pragma: no cover - defensive wrapping
            raise ExtractionError(f"Field '{field_name}' extraction failed: {exc}") from exc
