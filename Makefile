.DEFAULT_GOAL := help

VENV := .venv
PYTHON_FALLBACK := python3
ifeq ($(shell command -v python3.11 >/dev/null 2>&1 && echo yes),yes)
PYTHON := python3.11
else
PYTHON := $(PYTHON_FALLBACK)
endif

.PHONY: help venv dev install test coverage lint typecheck check clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-12s %s\n", $$1, $$2}'

venv: ## Create .venv if missing
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi

dev: venv ## Install package locally in editable mode with dev + llm dependencies
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/pip install -e ".[dev,llm]"
	@echo ""
	@echo "Development environment is ready in $(VENV)."
	@echo "Activate it in your current shell with:"
	@echo "  source $(VENV)/bin/activate"
	@echo "Or run CLI directly without activation:"
	@echo "  $(VENV)/bin/resume-parser --file resumes/CV_Taiseem.pdf --skills-mode fake"

install: dev ## Backward-compatible alias for dev setup

test: ## Run tests
	@if [ -x "$(VENV)/bin/pytest" ]; then \
		$(VENV)/bin/pytest -q; \
	else \
		$(PYTHON) -m pytest -q; \
	fi

coverage: ## Run tests with coverage report
	@if [ -x "$(VENV)/bin/pytest" ]; then \
		$(VENV)/bin/pytest -q --cov=app --cov-report=term-missing; \
	else \
		$(PYTHON) -m pytest -q --cov=app --cov-report=term-missing; \
	fi

lint: ## Run pylint on application code
	@if [ -x "$(VENV)/bin/pylint" ]; then \
		PYLINTHOME=.pylint.d $(VENV)/bin/pylint --jobs=1 src/app; \
	elif command -v pylint >/dev/null 2>&1; then \
		PYLINTHOME=.pylint.d pylint --jobs=1 src/app; \
	else \
		PYLINTHOME=.pylint.d $(PYTHON) -m pylint --jobs=1 src/app; \
	fi

typecheck: ## Run mypy on application code
	@if [ -x "$(VENV)/bin/mypy" ]; then \
		$(VENV)/bin/mypy src/app; \
	elif command -v mypy >/dev/null 2>&1; then \
		mypy src/app; \
	else \
		$(PYTHON) -m mypy src/app; \
	fi

check: lint typecheck coverage ## Run lint, typecheck, and tests with coverage

clean: ## Remove caches and build artifacts
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .pylint.d build dist
