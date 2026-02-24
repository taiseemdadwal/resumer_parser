"""Extractor abstraction and error types.

Field extractors are responsible for deriving one field value from plain resume text.
They remain independent from file format concerns, which are handled by parsers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_co = TypeVar("T_co", covariant=True)


class ExtractionError(Exception):
    """Raised when field extraction fails unexpectedly."""


class FieldExtractor(ABC, Generic[T_co]):
    """Generic contract for extracting a typed field from resume text.

    Implementations should avoid side effects and return a stable value for a given input.
    """

    @abstractmethod
    def extract(self, text: str) -> T_co:
        """Extract one field value from resume plain text.

        Implementations should return deterministic results for equivalent inputs.

        Args:
            text: Full resume text output from a parser.

        Returns:
            T_co: Extracted field value.

        Raises:
            ExtractionError: Implementations may raise when extraction fails unexpectedly.
        """
