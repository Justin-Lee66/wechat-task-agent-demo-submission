# LLM Smoke Test

## Purpose

The default demo path is deterministic `text_fixture` extraction and does not require secrets. The LLM smoke test is an optional local check for the OpenAI-backed `llm_text` or `llm_vision` extractor path.

## Local Setup

Copy the example env file and edit it locally:

```bash
cp .env.example .env
```

In `.env`, add your own key:

```bash
EXTRACTOR_MODE=llm_text
OPENAI_API_KEY=<your local OpenAI API key>
OPENAI_MODEL=gpt-5.5
```

`gpt-5.5` is the recommended OpenAI model for this demo's vision/text extraction path: it analyzes screenshot inputs and returns structured task data. Image generation models such as `gpt-image-2` are for generating or editing images, not for this extraction workflow.

The committed repository must not include `.env` or a real API key.

## Run The Smoke Test

```bash
make llm-smoke
```

Without `OPENAI_API_KEY`, the expected output is:

```text
llm-smoke skipped: OPENAI_API_KEY is not set.
```

With a key, the script runs the 10am fixture through the selected OpenAI extractor mode and writes:

```text
reports/llm_smoke_report.json
```

The report includes:

- provider
- mode
- model
- snapshot_id
- status
- extracted_task_count
- schema_valid
- fallback_used
- error_message, if any

It does not include raw API keys or large raw model output.

## Full Vision Baseline Comparison

For the full screenshot workflow, run:

```bash
make llm-vision-qa
```

This command requires a local `OPENAI_API_KEY`. It runs:

1. `text_fixture` full sequence as the baseline.
2. `llm_vision` for 10am, 12pm, and 2pm.
3. `text_fixture` for `done_update`, because the status update is demo-only text.

It writes:

```text
reports/extractor_compare_report.json
```

The comparison checks:

- total task count
- canonical task keys
- project counts
- status counts
- each viewer's assigned-task matrix
- each viewer's mention/visibility matrix
- Chinese localized dashboard title/description text for each canonical task

The expected healthy result is `total_tasks_match=true`, `canonical_keys_match=true`, `zh_display_text_match=true`, empty role diffs, empty Chinese display diffs, and no missing/extra canonical keys.

## Mode Selection

Default smoke behavior tests `llm_text`.

To test vision:

```bash
LLM_SMOKE_MODE=llm_vision make llm-smoke
```

or:

```bash
.venv/bin/python scripts/llm_smoke.py --mode llm_vision --snapshot-id 10am
```

`llm_text` uses `data/text_fallback/*.txt`. `llm_vision` uses the provided screenshots for `10am`, `12pm`, and `2pm`.

The demo-only `done_update` fixture has no screenshot and remains `text_fixture`.

## Dashboard Check

1. Start the app with `make demo`.
2. In the sidebar, choose `llm_text` or `llm_vision` from the Extractor dropdown.
3. Run a single ingest or Run Full Demo.
4. Inspect the Ingestion Run Log for the actual extractor mode.
5. If LLM extraction fails, the workflow falls back to `text_fixture` and records the fallback mode.

## Safety Checklist

Before committing:

```bash
git status --short
git ls-files .env '.env*'
git grep -n -E "OPENAI_API_KEY|sk-[A-Za-z0-9_-]{20,}" -- . ':!README.md' ':!docs/LLM_SMOKE_TEST.md' ':!.env.example'
```

Confirm:

- `.env` is not tracked.
- no real API key appears in diffs, docs, reports, or tests.
- `reports/llm_smoke_report.json`, if present, is concise and contains no secrets.
- `reports/extractor_compare_report.json`, if present, contains only counts, keys, and role matrices, never the API key.
