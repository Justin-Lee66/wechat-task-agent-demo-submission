# Debug Runbook

## App Does Not Start

Run:

```bash
make install
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Check that dependencies installed and that port `8000` is free.

## Dashboard Is Empty

Click `Run 10am ingest` or run:

```bash
.venv/bin/python - <<'PY'
from agent.workflow import AgentWorkflow
print(AgentWorkflow().ingest("10am"))
PY
```

## Reset State

Use the dashboard reset button or:

```bash
make reset
```

## Run Deterministic QA

```bash
make qa
```

The command resets the database, replays all snapshots, prints JSON, and writes `reports/demo_qa_report.json`.

Expected final demo counts:

- `total_tasks`: 17
- `status_count.done`: 5
- `status_count.todo`: 12
- `duplicate_canonical_keys`: []
- role completion checks for 阿可, Henry, Iris, Tara.L, and Chris: `true`

## Inspect Source Evidence

Open the dashboard, click a task's `View Evidence` button, and check the modal:

- raw source message text
- first/last seen snapshot
- source message hash count
- parsed due/assignee/mention fields
- screenshot preview when the snapshot is 10am, 12pm, or 2pm

For direct screenshot route checks:

```bash
curl -I http://127.0.0.1:8000/evidence/screenshot/2pm
```

## Debug Language Switch

The language preference is stored in browser `localStorage` as `dashboardLanguage`.

In the browser console:

```js
localStorage.removeItem("dashboardLanguage")
```

Reloading should return the UI to English.

## Verify Fixture Base Date

The fixture base is intentionally `2025-05-16T09:00:00`.

Check:

```bash
grep DEMO_BASE_DATETIME .env.example docker-compose.yml
grep DEFAULT_BASE_DATETIME agent/normalizer.py
```

Do not reinterpret the fixture as 2026. The screenshot deadlines Monday 5/19 and Tuesday 5/20 match the 2025 calendar.

## Fixture Date vs Local Run Time

The main dashboard intentionally shows only the fixture/simulation date:

- simulation date: fixed source context used for relative due parsing
- current snapshot: latest successful simulated ingest

Real local execution timestamps are still stored in ingestion logs and visible in the lower-priority Run Log.

## Verify Visual UI

1. Start the app with `make demo`.
2. Open http://127.0.0.1:8000.
3. Confirm the dark left sidebar is visible and the primary CTA is `Run Full Demo`.
4. Click `Run Full Demo` and watch the timeline progress through 10am, 12pm, 2pm, and status update.
5. Confirm the language dropdown displays the current language, then switch between `EN` and `中文`.
6. Confirm the sidebar only shows My Todo, Project Board, Needs Review, and Run Log.
7. Switch the Current user dropdown between 经理, 阿可, Henry, Iris, Tara.L, and Chris.
8. Confirm My Todo changes by selected viewer; Manager mode shows global priority work.
9. Use Project Board filters: All, Only {viewer}, and each project. These should filter, not scroll.
10. Confirm completed task cards are green in Manager and person views.
11. Confirm task cards show @others such as Henry, Tara.L, Iris, and Chris where present.
12. Confirm due display shows the original phrase and resolved due date, for example `3 天内 -> 2025-05-19 18:00`.
13. Open `View Evidence` and confirm the modal shows raw text, screenshot preview, and parsed fields.
14. Confirm the main dashboard does not show real 2026 runtime; local timestamps should appear only in logs.

## LLM Mode Falls Back

See `docs/LLM_SMOKE_TEST.md` for the full local smoke-test flow.

Confirm:

- In the dashboard sidebar, choose `llm_text` or `llm_vision` from the Extractor dropdown.
- If `OPENAI_API_KEY` is not set, the dashboard should show a toast reminder and should not start LLM extraction.
- Choose `text_fixture` again to return to the deterministic no-key demo path.
- If `OPENAI_API_KEY` is set, run an ingest and inspect the Ingestion Run Log for the actual `extractor_mode`.
- If an LLM call fails validation or raises an error, `ingestion_runs.error_message` should contain details and the run mode may show a text-fixture fallback.
- To compare the full vision path objectively, run `make llm-vision-qa` and inspect `reports/extractor_compare_report.json`. Healthy output has matching canonical keys, project counts, status counts, and empty role diffs.

Fallback to `text_fixture` is expected if validation or model calls fail.

The demo-only `done_update` stage always uses `text_fixture` because it has no screenshot source.
