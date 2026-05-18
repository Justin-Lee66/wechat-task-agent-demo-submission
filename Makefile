.PHONY: demo install test qa llm-smoke llm-vision-qa reset tree

PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -e ".[dev]"

demo: install
	$(BIN)/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

test:
	$(BIN)/pytest -q

qa:
	$(BIN)/python scripts/demo_qa.py

llm-smoke:
	$(BIN)/python scripts/llm_smoke.py

llm-vision-qa:
	$(BIN)/python scripts/extractor_compare.py --mode llm_vision

reset:
	rm -f data/tasks.db

tree:
	find . -path './.venv' -prune -o -path './__pycache__' -prune -o -type f -print | sort
