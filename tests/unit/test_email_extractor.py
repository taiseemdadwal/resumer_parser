"""Unit tests for EmailExtractor."""

from app.extractors.email_extractor import EmailExtractor


def test_extracts_first_email_from_text() -> None:
    """Extractor should return the first detected email address."""

    extractor = EmailExtractor()
    text = "Contact first@example.com or backup@example.org"

    assert extractor.extract(text) == "first@example.com"


def test_returns_none_when_email_absent() -> None:
    """Extractor should return None when no email pattern exists."""

    extractor = EmailExtractor()

    assert extractor.extract("No contact address in this text") is None
