# Architecture

## 1. Architectural Overview

This project is designed as a small, extensible framework with clear OOP boundaries:
- file parsing
- field extraction
- orchestration
- output model

The framework input is a resume file path (`.pdf` or `.docx`), and the output is:
- `name: str | None`
- `email: str | None`
- `skills: list[str]`

## 2. Design Principles

- Separation of concerns:
  - Parsers only convert files to plain text.
  - Extractors only derive field values from text.
  - Orchestrators only coordinate flow and error handling.
- Pluggability:
  - Parser/extractor implementations can be swapped without changing orchestration.
- Testability:
  - Core behavior is deterministic and testable offline.
- Minimalism:
  - Extra framework layers were intentionally avoided when not required.

## 3. Required Classes and Contracts

The exact required concepts and class names are implemented.

### Parser layer

- `FileParser` (abstract)
  - `can_parse(file_path: str) -> bool`
  - `parse(file_path: str) -> str`

Concrete implementations:
- `PDFParser`
- `WordParser`

### Extraction layer

- `FieldExtractor[T]` (generic abstract)
  - `extract(text: str) -> T`

Concrete implementations:
- `NameExtractor`
- `EmailExtractor`
- `SkillsExtractor`

### Domain model

- `ResumeData` as `@dataclass(frozen=True)`

### Coordinator

- `ResumeExtractor`
  - accepts a dictionary of field extractors
  - validates required keys (`name`, `email`, `skills`)
  - executes extractors and returns `ResumeData`

### Framework

- `ResumeParserFramework`
  - combines parser selection and resume extraction
  - exposes one parsing API:
    - `parse_resume(file_path: str) -> ResumeData`

## 4. Runtime Flow

```text
file_path
   |
   v
ResumeParserFramework.parse_resume(file_path)
   |
   v
select parser by suffix (can_parse)
   |
   v
PDFParser / WordParser -> plain text
   |
   v
ResumeExtractor.extract(text)
   |
   +--> NameExtractor.extract(text)
   +--> EmailExtractor.extract(text)
   +--> SkillsExtractor.extract(text)
   |
   v
ResumeData
```

## 5. OOP Collaboration Diagram

```text
                 +-----------------------------+
                 |      ResumeParserFramework  |
                 +-----------------------------+
                 | - _parsers: list[FileParser]
                 | - _resume_extractor
                 +-----------------------------+
                 | + parse_resume(file_path)   |
                 +-------------+---------------+
                               |
                               v
 +---------------------------- FileParser ----------------------------+
 |                        <<abstract class>>                         |
 +-------------------------------------------------------------------+
 | + can_parse(file_path) -> bool                                    |
 | + parse(file_path) -> str                                         |
 +----------------------+----------------------------+---------------+
                        |                            |
                        v                            v
                 +-------------+               +-------------+
                 |  PDFParser  |               | WordParser  |
                 +-------------+               +-------------+

                               parsed text
                                   |
                                   v
                     +-------------------------------+
                     |        ResumeExtractor        |
                     +-------------------------------+
                     | - _field_extractors: dict[...]|
                     +-------------------------------+
                     | + extract(text) -> ResumeData |
                     +---------------+---------------+
                                     |
                                     v
                +---------------- FieldExtractor[T] -----------------+
                |                  <<abstract class>>                |
                +----------------------------------------------------+
                | + extract(text) -> T                               |
                +-------------+------------------+-------------------+
                              |                  |
                              v                  v
                     +---------------+    +----------------+
                     | NameExtractor |    | EmailExtractor |
                     +---------------+    +----------------+
                              |
                              v
                     +----------------+
                     | SkillsExtractor|
                     +----------------+
                     | uses LLMClient |
                     +--------+-------+
                              |
                              v
                       +-------------+
                       | LLMClient   |
                       | (Protocol)  |
                       +-------------+
```

## 6. Strategy Choices and Why

### Name

- Implemented: rule-based `NameExtractor`
- Why:
  - deterministic
  - easy to reason about
  - fast for common resume layouts

### Email

- Implemented: regex `EmailExtractor`
- Why:
  - email is a structured pattern where regex is practical and reliable

### Skills

- Implemented: LLM-based `SkillsExtractor`
- Why:
  - assignment requires at least one ML/LLM-based strategy
  - skills extraction benefits from semantic interpretation

`SkillsExtractor` remains vendor-agnostic via an injected `LLMClient` protocol.
That allows:
- offline deterministic mode (`fake`, `stub`)
- real OpenAI mode (`llm`)

## 7. Error Handling

- `ParserError`
  - unsupported suffix
  - parser read/format failure
  - includes file path context

- `ExtractionError`
  - extractor failure or invalid output type
  - includes field context

Exception chaining is used where appropriate to preserve original failure causes.

## 8. Extensibility Path

### Add a new parser

1. Implement `FileParser`.
2. Add suffix logic in `can_parse`.
3. Add parser instance to framework composition in `main.py`.
4. Add tests.

### Add new extraction strategy for an existing field

1. Implement `FieldExtractor[T]`.
2. Register a strategy mode in the relevant factory map.
3. Add unit tests for normal and edge cases.

### Add a new field

1. Extend `ResumeData`.
2. Add required key handling in `ResumeExtractor`.
3. Add validation + tests.
4. Update CLI output/docs.

## 9. Testing Approach

Tests are separated into:
- `tests/unit`
- `tests/integration`

Coverage includes:
- parser correctness and parser error paths
- extractor correctness and normalization behavior
- coordinator orchestration and key validation
- framework end-to-end behavior
- CLI return codes and JSON output

All default tests run offline with deterministic behavior.

## 10. Operational Notes

- CLI command: `resume-parser`
- Setup: `make venv && make dev`
- Quality gate: `make check`
- Optional real LLM mode requires `OPENAI_API_KEY`
- `.env` loading is supported and compatible with manual exports

## 11. Diagnostics and Debug Flag

The CLI exposes a debug flag:

- `--debug`

Design intent:
- increase observability for framework composition and extraction flow
- avoid log noise from third-party libraries

Runtime behavior:
- sets `app.*` logger level to `DEBUG`
- keeps `pdfminer`, `httpx`, and `openai` logs at warning level
- shows stack traces for runtime failures in CLI execution paths
