"""Unit tests for PDFParser."""

from pathlib import Path

from reportlab.pdfgen import canvas

from app.parsers.base import ParserError
from app.parsers.pdf_parser import PDFParser


def _create_pdf(path: Path) -> None:
    pdf = canvas.Canvas(str(path))
    pdf.drawString(100, 750, "Jane Doe")
    pdf.drawString(100, 730, "jane@example.com")
    pdf.save()


def test_pdf_parser_extracts_text(tmp_path: Path) -> None:
    """PDF parser should extract visible strings from a generated PDF."""

    path = tmp_path / "resume.pdf"
    _create_pdf(path)

    parser = PDFParser()
    parsed = parser.parse(str(path))

    assert "Jane Doe" in parsed
    assert "jane@example.com" in parsed


def test_pdf_parser_can_parse_pdf_suffix_case_insensitive() -> None:
    """PDF parser should match suffix regardless of casing."""

    parser = PDFParser()

    assert parser.can_parse("resume.PDF")


def test_pdf_parser_raises_parser_error_for_missing_file() -> None:
    """PDF parser should raise ParserError when the target file cannot be opened."""

    parser = PDFParser()

    try:
        parser.parse("does_not_exist.pdf")
    except ParserError as exc:
        assert "does_not_exist.pdf" in str(exc)
    else:
        raise AssertionError("Expected ParserError for missing file")
