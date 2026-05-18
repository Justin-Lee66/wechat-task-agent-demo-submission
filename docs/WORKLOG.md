# Implementation Summary

This file is a concise implementation record for reviewer context. It summarizes the final capabilities and verification targets for the demo.

## Core Demo

- Built a local FastAPI + Jinja2 + SQLite application for ingesting cumulative WeChat snapshots.
- Added deterministic text fixtures for the provided 10am, 12pm, and 2pm screenshots, plus a clearly labeled demo-only status update fixture.
- Implemented typed extraction models, due-date normalization, status keyword detection, mention handling, task dedupe, and incremental task merging.
- Preserved a stable API-key-free demo path through `EXTRACTOR_MODE=text_fixture`.

## Data And Dedupe

- Message-level dedupe uses normalized raw message hashes.
- Task-level dedupe uses stable canonical keys such as `solene|main-visual-poster-first-version`.
- Later snapshots can enrich existing tasks instead of creating duplicates.
- The demo validates the expected full sequence at 17 tasks, 0 duplicate canonical keys, and 5 completed tasks after the status update fixture.

## Dashboard

- Designed an Acre-style operations cockpit with a dark sidebar and focused main content.
- Added staged `Run Full Demo`, collapsed manual controls, auto-refresh, bilingual UI, role viewer mode, and extractor mode selection.
- Organized the main user flow around My Todo, Project Board, Team Review Queue, and Run Log.
- Added evidence modals with raw source messages, parsed fields, message hash count, and screenshot previews.
- Kept selected-viewer highlighting separate from neutral @others visibility.

## Role Semantics

- The viewer selector supports Manager / 经理, 阿可, Henry, Iris, Tara.L, and Chris.
- Person views show assigned work in My Todo and viewer-aware KPI labels.
- Manager view shows global work without @Me highlighting.
- Mention-only broadcasts remain visible but do not become personal todos unless a viewer is explicitly assigned.
- `@mkt Chris` is normalized as `mkt Chris`, with `mkt` treated as a role prefix rather than a separate user.

## LLM Path

- Optional `llm_text` and `llm_vision` modes use the same structured schema and prompt rules as the deterministic baseline.
- LLM extraction is optional and requires a local `OPENAI_API_KEY`; no API key is committed.
- The prompt covers bullet-level mention scoping, broadcast language, context references, Admin / Task Ops enrichment, and conservative assignment handling.
- LLM outputs are normalized into the same project/task taxonomy before persistence.
- `make llm-smoke` and `make llm-vision-qa` provide optional live checks when a local API key is available.

## Verification

Recommended reviewer commands:

```bash
make test
make qa
make llm-smoke
```

Optional live vision comparison with a local API key:

```bash
make llm-vision-qa
```

Expected deterministic QA invariants:

- `total_tasks = 17`
- `duplicate_canonical_keys = []`
- `missing_expected_canonical_keys = []`
- `status_count.done = 5`
- Solene main visual remains one merged task.
- 1847 Hudson Blvd arrival/address work remains one merged task.
- Role-specific completion checks for 阿可, Henry, Iris, Tara.L, and Chris are true.
