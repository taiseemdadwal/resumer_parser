"""Parser abstractions and errors.

Parsers convert file content into plain text. The framework can then apply field-specific
extractors to that plain text independently of source file format.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ParserError(Exception):
    """Raised when parser selection fails or a parser cannot read/convert a file."""


class FileParser(ABC):
    """Contract for converting a specific file type into plain text.

    Implementations should be stateless and deterministic for a given file input.
    They must raise :class:`ParserError` (or an exception wrapped by the framework)
    when parsing cannot be completed.
    """

    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Decide whether the parser can handle a file path.

        Implementations should rely on suffix or lightweight path inspection only.

        Args:
            file_path: Resume file path provided by the caller.

        Returns:
            bool: ``True`` when the parser supports the given path.

        Raises:
            None.
        """

    @abstractmethod
    def parse(self, file_path: str) -> str:
        """Extract plain text from a supported file path.

        Implementations convert file content into plain text for field extractors.

        Args:
            file_path: Resume file path to parse.

        Returns:
            str: Extracted plain-text content.

        Raises:
            ParserError: If file reading or format parsing fails.
        """
