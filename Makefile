.PHONY: install lint check-fmt check-ruff check-mypy

ifdef GITHUB_ACTIONS
RUFF_ARGS := --output-format=github
endif

install:
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/pip install poetry
	.venv/bin/poetry install --no-root

lint: check-fmt check-ruff check-mypy

check-fmt:
	.venv/bin/ruff format . --check

check-ruff:
	.venv/bin/ruff request_mapper $(RUFF_ARGS)

check-mypy:
	.venv/bin/mypy request_mapper --strict

format:
	.venv/bin/ruff format .
