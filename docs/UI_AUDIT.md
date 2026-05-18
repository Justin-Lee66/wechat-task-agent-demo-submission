# UI Audit

This audit records the intended dashboard experience and the acceptance checks used for the current demo UI.

## Experience Goals

- Present the app as a calm operations cockpit, not a raw database table.
- Keep the primary workflow obvious: run the demo, inspect assigned work, review project boards, audit fuzzy tasks, and check run logs only when needed.
- Keep the main dashboard aligned to the fixture simulation date instead of local runtime.
- Hide technical evidence until the reviewer explicitly opens a task evidence modal.
- Make role context clear without adding a heavy user-management system.

## Current Layout

- Dark Acre-inspired left sidebar with logo, demo state, current viewer, extractor mode, and section navigation.
- Main workspace ordered as cockpit header, KPI row, My Todo / Priority Todo, Project Board, Team Review Queue, and Run Log.
- Primary `Run Full Demo` button with manual controls collapsed by default.
- Project Board grouped by project with filters for All, Only {viewer}, and each project.
- Evidence modal showing raw source messages, screenshot preview, parsed fields, source hash count, and task metadata.

## Interaction Checks

- `Run Full Demo` remains the most prominent action.
- Manual controls remain available but secondary.
- Sidebar dropdowns for Current user and Extractor fit the sidebar and preserve spacing.
- Language dropdown displays the current language and switches visible UI text.
- Project filters filter the board rather than only scrolling.
- Team Review Queue stays global and clearly separate from personal My Todo.
- Run Log remains low priority and available for auditing ingestion behavior.
- Main task panels scroll with the page; evidence modal may scroll internally.

## Role Checks

- Manager / 经理 shows global open work and no @Me card highlight.
- 阿可, Henry, Iris, Tara.L, and Chris views show only assigned work in My Todo.
- Mention-only notifications remain visible on cards but do not enter My Todo.
- Selected-viewer chips are highlighted; other assignee/mention chips stay neutral and visible.
- Completed task cards use green/healthy styling, overriding warm selected-viewer card backgrounds.

## Evidence Checks

- Every deterministic text-fixture task has screenshot-backed evidence from 10am, 12pm, or 2pm after the full demo sequence.
- Demo-only `done_update` messages remain clearly labeled as status update fixture text.
- Status update evidence does not hide the latest real screenshot-backed source message.
- Admin / Task Ops evidence includes both the direct follow-up instruction and the previous Year-end Summit context message.

## LLM UI Checks

- `text_fixture` remains the default no-key extractor mode.
- Selecting `llm_text` or `llm_vision` without a configured local key shows a clear warning and does not start extraction.
- Actual extractor modes and fallback labels remain visible in the Ingestion Run Log.
- `llm_vision` output is compared against the deterministic baseline through `make llm-vision-qa` when a local API key is available.

## Verification Commands

```bash
make test
make qa
make llm-smoke
```

Optional with a local OpenAI API key:

```bash
make llm-vision-qa
```

Current deterministic acceptance target:

- 17 total tasks.
- 0 duplicate canonical keys.
- 0 missing expected canonical keys.
- 5 completed tasks after the demo-only status update fixture.
- Matching Solene and 1847 Hudson Blvd merge checks.
