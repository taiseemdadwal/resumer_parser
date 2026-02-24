"""Unit tests for NameExtractor."""

from app.extractors.name_extractor import NameExtractor


def test_name_extractor_finds_top_line_name() -> None:
    """Extractor should identify a clear name in the first line."""

    extractor = NameExtractor()
    text = "Jane Doe\nEmail: jane.doe@example.com\nSummary\nExperienced engineer"

    assert extractor.extract(text) == "Jane Doe"


def test_name_extractor_skips_heading_and_finds_next_name() -> None:
    """Extractor should ignore heading lines before selecting a name candidate."""

    extractor = NameExtractor()
    text = "RESUME\nJane Doe\nEmail: jane.doe@example.com"

    assert extractor.extract(text) == "Jane Doe"


def test_name_extractor_returns_none_when_no_candidate() -> None:
    """Extractor should return None when lines do not match name heuristics."""

    extractor = NameExtractor()
    text = "RESUME\nSUMMARY\nEXPERIENCE\nemail@example.com\n12345"

    assert extractor.extract(text) is None


def test_name_extractor_supports_name_prefix() -> None:
    """Extractor should normalize and parse a line starting with ``Name:``."""

    extractor = NameExtractor()
    text = "Name: Jane Doe\nEmail: jane.doe@example.com"

    assert extractor.extract(text) == "Jane Doe"


def test_name_extractor_rejects_single_word_candidate() -> None:
    """Extractor should reject candidates that do not have 2-4 words."""

    extractor = NameExtractor()
    text = "Madonna\nEmail: madonna@example.com"

    assert extractor.extract(text) is None
