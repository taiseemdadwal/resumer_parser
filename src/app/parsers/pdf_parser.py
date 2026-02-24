"""PDF parser implementation based on ``pdfminer.six``."""

from __future__ import annotations

import re
from pathlib import Path

from pdfminer.high_level import extract_text
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFSyntaxError

from .base import FileParser, ParserError

_BLANK_LINES = re.compile(r"\n{3,}")


class PDFParser(FileParser):
    """Extract plain text from PDF documents.

    The parser normalizes output by trimming trailing spaces on each line and collapsing
    excessive blank-line runs.
    """

    def can_parse(self, file_path: str) -> bool:
        """Check whether this parser supports the provided file path.

        This method performs case-insensitive suffix matching for PDF files.

        Args:
            file_path: Candidate file path.

        Returns:
            bool: ``True`` when path suffix is ``.pdf`` (case-insensitive).

        Raises:
            None.
        """

        return Path(file_path).suffix.lower() == ".pdf"

    def parse(self, file_path: str) -> str:
        """Parse PDF content into normalized plain text.

        Extracted text is normalized for downstream regex and heuristic extraction.

        Args:
            file_path: Path to a PDF file.

        Returns:
            str: Normalized plain-text content extracted from the PDF.

        Raises:
            ParserError: If the PDF cannot be opened or parsed.
        """

        try:
            extracted = extract_text(file_path)
        except (OSError, PDFSyntaxError, PDFTextExtractionNotAllowed, ValueError) as exc:
            raise ParserError(f"Failed to parse PDF file '{file_path}': {exc}") from exc

        lines = [line.rstrip() for line in extracted.splitlines()]
        normalized = "\n".join(lines).strip()
        return _BLANK_LINES.sub("\n\n", normalized)
