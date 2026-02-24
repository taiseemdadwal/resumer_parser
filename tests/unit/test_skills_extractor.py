"""Unit tests for SkillsExtractor with offline fake clients."""

from app.extractors.skills_extractor import LLMClient, SkillsExtractor


class FakeLLMClient(LLMClient):
    """Deterministic fake LLM used to keep tests offline."""

    def __init__(self, response: str) -> None:
        self._response = response

    def complete(self, prompt: str) -> str:
        _ = prompt
        return self._response


def test_skills_extractor_parses_json_and_normalizes() -> None:
    """Extractor should trim, deduplicate, and keep skill order."""

    extractor = SkillsExtractor(FakeLLMClient('["Python", "LLM", "python", " SQL ", ""]'))

    assert extractor.extract("ignored by fake") == ["Python", "LLM", "SQL"]


def test_skills_extractor_handles_wrapped_array_text() -> None:
    """Extractor should recover the first JSON array from noisy responses."""

    extractor = SkillsExtractor(FakeLLMClient('Here you go: ["Python", "LLM"]'))

    assert extractor.extract("resume text") == ["Python", "LLM"]


def test_skills_extractor_returns_empty_when_no_array_found() -> None:
    """Extractor should return empty list when response has no JSON array fragment."""

    extractor = SkillsExtractor(FakeLLMClient("No structured output here"))

    assert extractor.extract("resume text") == []


def test_skills_extractor_returns_empty_for_non_array_json() -> None:
    """Extractor should reject valid JSON payloads that are not arrays."""

    extractor = SkillsExtractor(FakeLLMClient('{"skills": "Python"}'))

    assert extractor.extract("resume text") == []


def test_skills_extractor_handles_unbalanced_array_fragment() -> None:
    """Extractor should return empty list when array fragment cannot be balanced."""

    extractor = SkillsExtractor(FakeLLMClient('Result: ["Python", "LLM"'))

    assert extractor.extract("resume text") == []


def test_skills_extractor_caps_output_length() -> None:
    """Extractor should cap normalized output at the configured maximum count."""

    skills = [f"Skill{i}" for i in range(40)]
    payload = "[" + ", ".join(f'\"{skill}\"' for skill in skills) + "]"
    extractor = SkillsExtractor(FakeLLMClient(payload))

    assert len(extractor.extract("resume text")) == 30
