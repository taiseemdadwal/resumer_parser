# Resume Parser Framework

This repository contains a take-home submission for a resume parsing framework with a clean, object-oriented architecture and strict separation of concerns.

The system parses `.pdf` and `.docx` resumes and returns structured output:
- `name: str | None`
- `email: str | None`
- `skills: list[str]`

Detailed design decisions, tradeoffs, and diagrams are documented in `Architecture.md`.

## Implemented Scope

- `FileParser` abstraction with concrete `PDFParser` and `WordParser`
- `FieldExtractor[T]` abstraction with concrete:
  - `NameExtractor` (rule-based heuristic)
  - `EmailExtractor` (regex)
  - `SkillsExtractor` (LLM-based strategy via `LLMClient` dependency injection)
- `ResumeData` as a frozen dataclass
- `ResumeExtractor` as a dictionary-driven coordinator
- `ResumeParserFramework` with required API:
  - `parse_resume(file_path: str) -> ResumeData`
- CLI command: `resume-parser`

## Requirements

- Python `3.11+`
- macOS/Linux shell

## Setup and Verification

```bash
make dev
source .venv/bin/activate
```

`make dev` creates `.venv` (if missing) and installs all project dependencies in that environment.

Run the full quality gate:

```bash
make check
```

## CLI Usage

```bash
resume-parser --file <path/to/resume.pdf|path/to/resume.docx> [options]
```

Options:
- `--name-mode rule|stub` (default: `rule`)
- `--email-mode regex|stub` (default: `regex`)
- `--skills-mode fake|stub|llm` (default: `fake`)
- `--debug` (enables debug logs for `app.*` modules)

Examples:

```bash
# Offline deterministic mode
resume-parser --file resumes/CV_Taiseem.pdf --skills-mode fake

# Baseline mode (no skills extraction)
resume-parser --file resumes/CV_Taiseem.pdf --skills-mode stub

# Real LLM mode (OpenAI-backed)
resume-parser --file resumes/CV_Taiseem.pdf --skills-mode llm

# Troubleshooting mode with debug logs
resume-parser --file resumes/CV_Taiseem.pdf --skills-mode fake --debug
```

Exit Codes:
- `0`: success
- `1`: runtime error (parser/extraction/config)
- `2`: argument/usage error

## Debug Mode

The CLI provides a `--debug` flag for troubleshooting parser and extraction orchestration.

Behavior in debug mode:
- application logs (`app.*`) are set to `DEBUG`
- verbose third-party internals remain suppressed (`pdfminer`, `httpx`, `openai` stay at warning level)
- stack traces are included for runtime failures

This keeps diagnostics actionable without flooding output with low-level parser internals.

## Skills Modes

- `fake`: offline deterministic LLM-like strategy (good for demos/tests)
- `stub`: always returns `[]`
- `llm`: uses `OpenAILLMClient`

Default behavior is offline-safe and deterministic.

## Environment Configuration

Environment loading supports both shell exports and `.env` files:
- exported variables take precedence
- `.env` fills missing variables only

Variables:
- `OPENAI_API_KEY` (required for `--skills-mode llm`)
- `OPENAI_MODEL` (optional, default `gpt-4o-mini`)

Example `.env`:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Python API Example

```python
from app.extractors.email_extractor import EmailExtractor
from app.extractors.name_extractor import NameExtractor
from app.extractors.skills_extractor import LLMClient, SkillsExtractor
from app.framework import ResumeParserFramework
from app.parsers.pdf_parser import PDFParser
from app.parsers.word_parser import WordParser
from app.resume_extractor import ResumeExtractor


class FakeLLMClient(LLMClient):
    def complete(self, prompt: str) -> str:
        _ = prompt
        return '["Python", "LLM"]'


framework = ResumeParserFramework(
    parsers=[PDFParser(), WordParser()],
    resume_extractor=ResumeExtractor(
        {
            "name": NameExtractor(),
            "email": EmailExtractor(),
            "skills": SkillsExtractor(FakeLLMClient()),
        }
    ),
)

result = framework.parse_resume("resumes/example.docx")
print(result.to_dict())
```

## Development Commands

```bash
make lint
make typecheck
make test
make coverage
make check
make clean
```

## Project Structure

```text
src/app/
  domain/models.py                # ResumeData
  parsers/base.py                 # FileParser, ParserError
  parsers/pdf_parser.py           # PDFParser
  parsers/word_parser.py          # WordParser
  extractors/base.py              # FieldExtractor[T], ExtractionError
  extractors/name_extractor.py    # NameExtractor
  extractors/email_extractor.py   # EmailExtractor
  extractors/skills_extractor.py  # SkillsExtractor, LLMClient
  extractors/openai_llm_client.py # Optional OpenAI adapter
  resume_extractor.py             # Coordinator
  framework.py                    # Orchestration
  main.py                         # CLI composition root
```

## Submission Notes

- Class names and responsibilities are aligned with the assignment requirements.
- An LLM-based strategy is implemented for at least one field (`skills`) while tests remain offline by default.
- The architecture is intentionally minimal and extensible without unnecessary framework layers.
