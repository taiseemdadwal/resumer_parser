"""Unit tests for ResumeExtractor validation and error handling paths."""

from __future__ import annotations

import pytest

from app.extractors.base import ExtractionError
from app.extractors.base import FieldExtractor
from app.extractors.email_extractor import EmailExtractor
from app.extractors.name_extractor import NameExtractor
from app.extractors.skills_extractor import LLMClient, SkillsExtractor
from app.resume_extractor import ResumeExtractor


class _FakeLLM(LLMClient):
    def complete(self, prompt: str) -> str:
        _ = prompt
        return '["Python"]'


class _BadNameExtractor(FieldExtractor[object]):
    def extract(self, text: str) -> object:
        _ = text
        return 123


class _BadEmailExtractor(FieldExtractor[object]):
    def extract(self, text: str) -> object:
        _ = text
        return 123


class _BadSkillsExtractor(FieldExtractor[object]):
    def extract(self, text: str) -> object:
        _ = text
        return ["Python", 3]


class _RaisingExtractor(FieldExtractor[object]):
    def extract(self, text: str) -> object:
        _ = text
        raise RuntimeError("boom")


def _valid_extractors() -> dict[str, FieldExtractor[object]]:
    return {
        "name": NameExtractor(),
        "email": EmailExtractor(),
        "skills": SkillsExtractor(_FakeLLM()),
    }


def test_resume_extractor_to_dict_path() -> None:
    """Coordinator should return dataclass output that supports ``to_dict``."""

    extractor = ResumeExtractor(_valid_extractors())
    result = extractor.extract("Jane Doe\nEmail: jane@example.com")

    payload = result.to_dict()
    assert payload["name"] == "Jane Doe"


def test_resume_extractor_rejects_invalid_name_type() -> None:
    extractors = _valid_extractors()
    extractors["name"] = _BadNameExtractor()

    with pytest.raises(ExtractionError, match="Name extractor returned invalid type"):
        ResumeExtractor(extractors).extract("x")


def test_resume_extractor_rejects_invalid_email_type() -> None:
    extractors = _valid_extractors()
    extractors["email"] = _BadEmailExtractor()

    with pytest.raises(ExtractionError, match="Email extractor returned invalid type"):
        ResumeExtractor(extractors).extract("x")


def test_resume_extractor_rejects_invalid_skills_type() -> None:
    extractors = _valid_extractors()
    extractors["skills"] = _BadSkillsExtractor()

    with pytest.raises(ExtractionError, match="Skills extractor returned invalid type"):
        ResumeExtractor(extractors).extract("x")


def test_resume_extractor_wraps_field_error_with_field_name() -> None:
    extractors = _valid_extractors()
    extractors["email"] = _RaisingExtractor()

    with pytest.raises(ExtractionError, match="Field 'email' extraction failed"):
        ResumeExtractor(extractors).extract("x")
