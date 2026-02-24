"""Top-level framework orchestration for parsing resumes from files."""

from __future__ import annotations

import logging

from app.domain.models import ResumeData
from app.parsers.base import FileParser, ParserError
from app.resume_extractor import ResumeExtractor

logger = logging.getLogger(__name__)


class ResumeParserFramework:
    """Combine parser selection and field extraction into one entry point.

    The framework delegates file-to-text conversion to the first matching parser and then
    delegates text-to-structured-data conversion to ``ResumeExtractor``.
    """

    def __init__(self, parsers: list[FileParser], resume_extractor: ResumeExtractor) -> None:
        """Initialize framework with parser candidates and extraction coordinator.

        Parser instances are evaluated in order, allowing explicit precedence control.

        Args:
            parsers: Ordered parser candidates used for suffix-based selection.
            resume_extractor: Coordinator for text-to-structured extraction.

        Returns:
            None.

        Raises:
            None.
        """

        self._parsers = parsers
        self._resume_extractor = resume_extractor

    def parse_resume(self, file_path: str) -> ResumeData:
        """Parse a resume file and return structured data.

        The first parser whose ``can_parse`` method returns ``True`` is selected.

        Args:
            file_path: Path to a resume file. Suffix determines parser selection.

        Returns:
            ResumeData: Structured extraction output from parsed resume text.

        Raises:
            ParserError: If no parser can handle the suffix or parser execution fails.
        """

        logger.debug(
            "Attempting to parse file '%s' with %d parser candidates",
            file_path,
            len(self._parsers),
        )
        parser = next(
            (candidate for candidate in self._parsers if candidate.can_parse(file_path)),
            None,
        )
        if parser is None:
            raise ParserError(f"No parser available for file: {file_path}")

        logger.info("Selected parser '%s' for file '%s'", parser.__class__.__name__, file_path)
        text = parser.parse(file_path)
        logger.debug("Parser '%s' produced %d characters", parser.__class__.__name__, len(text))
        return self._resume_extractor.extract(text)
