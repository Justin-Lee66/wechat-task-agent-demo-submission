# wechat-task-agent-demo

A compact AI workflow demo for an AI maintenance / marketing operations take-home. The app ingests cumulative WeChat group snapshots, extracts structured tasks, deduplicates repeated messages/tasks, persists state in SQLite, and renders an Acre-style operations cockpit grouped by project.

The default demo uses text fallback fixtures, so it runs without an LLM API key.

## Quick Start: Local Dashboard

GitHub hosts the source code only. It does not host the running dashboard. To see the app, clone the repo, start the local FastAPI server, then open `localhost` in your browser.

From a terminal:

```bash
git clone https://github.com/Justin-Lee66/wechat-task-agent-demo-submission.git
cd wechat-task-agent-demo-submission
make demo
```

Keep that terminal running. When the server is ready, open:

```text
http://127.0.0.1:8000
```

Then click:

1. `Run Full Demo` to replay the full sequence with staged 8-second pauses.
2. Or expand `Manual Controls` for 10am, 12pm, 2pm, and the demo-only status update.
3. Open `View Evidence` on any task to inspect the raw source message and screenshot preview in a modal.

Docker alternative:

```bash
git clone https://github.com/Justin-Lee66/wechat-task-agent-demo-submission.git
cd wechat-task-agent-demo-submission
docker compose up --build
```

Then open the same local URL:

```text
http://127.0.0.1:8000
```

Run tests:

```bash
make install
make test
make qa
```

## Optional LLM Vision Setup

The stable default mode is `text_fixture` and does not require any API key. To test screenshot-based extraction, create a local `.env` file and add your own OpenAI API key. The real `.env` file is ignored by git and should not be committed.

```bash
cp .env.example .env
```

Edit `.env` locally:

```bash
DEMO_BASE_DATETIME=2025-05-16T09:00:00
EXTRACTOR_MODE=text_fixture
DATABASE_PATH=data/tasks.db

OPENAI_API_KEY=<your OpenAI API key>
OPENAI_MODEL=gpt-5.5
```

Start the app:

```bash
make demo
```

In the dashboard sidebar, use the `Extractor` dropdown:

- `text_fixture`: deterministic, API-key-free default.
- `llm_text`: LLM extraction from the text fallback fixtures.
- `llm_vision`: LLM extraction from the 10am / 12pm / 2pm screenshot fixtures.

For the full dashboard demo, select `llm_vision`, click `Run Full Demo`, and the screenshot stages will use the optional OpenAI vision path. The demo-only `done_update` stage always uses `text_fixture` because it has no screenshot.

Optional command-line checks:

```bash
make llm-smoke
make llm-vision-qa
```

`make llm-vision-qa` compares the live `llm_vision` result against the deterministic `text_fixture` baseline, including canonical keys, project counts, status counts, role assignee/mention matrices, and Chinese display text parity.

The `done_update.txt` fixture is demo-only. It exists because the provided screenshots do not include explicit completed-status updates; the demo uses it to prove keyword-triggered status changes across multiple viewer roles.

## Verification

Use the deterministic QA command to replay the full fixture sequence and generate an objective report:

```bash
make test
make qa
make llm-smoke
```

Optional live LLM vision comparison after adding a local `OPENAI_API_KEY`:

```bash
make llm-vision-qa
```

`make qa` resets `data/tasks.db`, ingests `10am`, `12pm`, `2pm`, then the demo-only `done_update`, prints JSON to stdout, and writes `reports/demo_qa_report.json`.

`make llm-smoke` skips gracefully when `OPENAI_API_KEY` is not set.

`make llm-vision-qa` is optional and uses a local `OPENAI_API_KEY`. It runs the full `llm_vision` flow against the deterministic `text_fixture` baseline and compares canonical keys, project counts, status counts, role-level assignee/mention matrices, and Chinese display text parity.

Sample QA output:

```json
{
  "belmont_youtube_done_after_update": true,
  "ake_completion_done": true,
  "henry_completion_done": true,
  "iris_completion_done": true,
  "tara_completion_done": true,
  "chris_completion_done": true,
  "duplicate_canonical_keys": [],
  "missing_expected_canonical_keys": [],
  "needs_review_count": 13,
  "self_task_count": 8,
  "solene_main_visual_merged_into_one_task": true,
  "hudson_blvd_description_map_merged_into_one_task": true,
  "status_count": {
    "done": 5,
    "todo": 12
  },
  "total_tasks": 17
}
```

## Problem Statement

Marketing operations work often arrives as cumulative chat screenshots. This demo shows a safe, reviewer-friendly alternative to a real WeChat integration:

- Read provided screenshots or text snapshots.
- Extract actionable work items into a typed schema.
- Normalize due dates, mentions, status keywords, and self mentions.
- Deduplicate cumulative messages and canonical tasks.
- Incrementally enrich earlier tasks when later messages add details.
- Show the result in a polished Acre-style dashboard with a clear full-demo workflow.

## Default Text Fallback

The app starts in `EXTRACTOR_MODE=text_fixture`. It reads files in `data/text_fallback/` and uses a deterministic parser tuned to the assignment fixtures. This makes the demo stable during review and avoids requiring secrets.

Screenshots are still stored under `data/screenshots/` for optional LLM vision mode.

## Demo UX

- The dashboard uses a calm two-column cockpit: a dark left sidebar for demo state/navigation and a focused main workspace for workflow review.
- `Run Full Demo` resets the database and then replays 10am -> 12pm -> 2pm -> status update with visible progress.
- `Manual Controls` is collapsed by default so the primary path is clear.
- The language dropdown displays the current language (`EN` or `中文`), switches English/Chinese UI text, and persists the preference in `localStorage`.
- The sidebar includes a compact role viewer dropdown: Manager / 经理, 阿可, Henry, Iris, Tara.L, and Chris.
- Person views scope My Todo and KPI labels to tasks where the selected viewer is an assignee: My tasks, My due today, My review, and My done.
- Manager view shows global open work, uses no @Me highlight, and keeps completed tasks as green/healthy cards.
- The main flow is user-centered: My Todo, Project Board, Team Review Queue, then Run Log.
- Project Board is grouped by project and filterable by All, Only {viewer}, and project-specific chips.
- Team Review Queue shows global fuzzy tasks across projects and is not limited to the selected viewer.
- Task cards show assignees, mentioned users, selected-viewer highlighting for assigned work, neutral @others chips, source time, and due text plus resolved due date.
- Completed task cards use green/healthy styling; unfinished selected-viewer tasks keep the warmer attention highlight.
- Source evidence opens in a modal and shows raw extracted WeChat text, parsed fields, source message hash count, and a compact screenshot preview.
- Exact screenshot cropping is a production extension once OCR/vision bounding boxes are available.

The dashboard supports a demo viewer selector. 阿可 is the default viewer.

Mention normalization treats `@mkt Chris` as one person label, `mkt Chris`; `mkt` is a marketing role prefix, not a separate user. The Chris viewer role maps to that label.

Group broadcast language such as `给大家同步` is treated as a task-level mention of all demo person viewers. For example, the Year-end Summit deadline message mentions all viewers for visibility, while the tasks still remain unassigned and stay in Team Review Queue until an owner is confirmed.

Mentions alone do not make a personal todo. A notification-style task can mention a viewer and still stay out of that viewer's My Todo until the viewer is explicitly assigned as an owner.

The deterministic parser also resolves narrow context references. In the 2pm fixture, `这些都同步进我们的任务表` refers to the immediately previous Year-end Summit deadline list, so the standalone Admin / Task Ops task is enriched with that context and its evidence includes both source messages.

## Optional LLM Extraction Test

Default mode is still `text_fixture`, so the submitted repo runs without any API key.

Optional LLM modes use the OpenAI API. The default configured model is `gpt-5.5` via `OPENAI_MODEL`, and it can be changed locally in `.env`. For this demo, `gpt-5.5` is the preferred vision/text extraction model because the task is image understanding plus structured text output.

To test locally:

```bash
cp .env.example .env
```

Then edit `.env` on your machine:

```bash
EXTRACTOR_MODE=llm_text
OPENAI_API_KEY=<your local OpenAI API key>
OPENAI_MODEL=gpt-5.5
```

Run:

```bash
make llm-smoke
make demo
```

The dashboard sidebar also includes an `Extractor` dropdown:

- `text_fixture`: default, deterministic, and API-key-free.
- `llm_text`: reads the text fallback fixtures through the optional LLM extractor.
- `llm_vision`: reads screenshot fixtures for 10am, 12pm, and 2pm through the optional LLM extractor.

`llm_text` and `llm_vision` require `OPENAI_API_KEY`. If the key is missing, the dashboard shows a clear reminder and does not start LLM extraction. The demo-only `done_update` stage always uses `text_fixture` because it has no source screenshot and exists only to demonstrate status keyword updates.

The LLM path uses the OpenAI Responses API with Pydantic structured output (`ExtractionResult`), retries up to two times after the first failure, and falls back to the deterministic text parser if extraction fails. `make llm-smoke` writes `reports/llm_smoke_report.json` only when a live key is configured.

The actual extractor mode, including any fallback such as `text_fixture_fallback_after_llm_text`, is recorded in the Ingestion Run Log.

LLM outputs are also normalized against the same project/task taxonomy used by `text_fixture`. This protects the demo from vision wording drift such as `Social Media` vs `Social Content`, `Company Website / Agent Portal` vs `Company Blog / Agent Front Desk`, or multiple phrasings of the same 1847 Hudson Blvd arrival/address task.

The committed repo never includes a real `.env` or API key.

## Architecture

```text
Input Adapter
  text fixtures / screenshot fixtures
        |
Extractor Layer
  deterministic parser by default
  optional OpenAI text / vision extractor
        |
Normalization Layer
  due parsing, mentions, self aliases, status keywords
        |
Persistence Layer
  SQLite: ingestion_runs, messages, tasks, task_events
        |
Dashboard Layer
  FastAPI + Jinja2 + vanilla JS polling
```

## Data Model

- `ingestion_runs`: snapshot id, extractor mode, status, counts, timestamps, errors.
- `messages`: source time, sender, raw text, unique raw hash.
- `tasks`: canonical key, project, title, description, assignees, mentions, due, status, review flags, raw message hashes.
- `task_events`: created/updated events for auditing incremental behavior.

## Dedupe Strategy

Message-level dedupe uses `raw_message_hash = sha256(source_time + sender + normalized raw_text)`.

Task-level dedupe uses:

```text
project_slug|canonical_title_slug
```

Examples:

- `solene|main-visual-poster-first-version`
- `belmont|yoyo-jason-youtube-video`
- `1847-hudson-blvd|arrival-map-address-description`

When a later message expands an earlier task, the upsert keeps the same canonical key and merges richer fields such as description, due date, assignees, mentions, status, and source hashes.

Optional LLM modes go through the same canonical taxonomy before persistence, so semantically equivalent model outputs merge into the same keys as the deterministic baseline.

## Dashboard Features

- KPI cards: total tasks, viewer/global work count, due today, review count, done count.
- Left sidebar: demo state, current snapshot, simulation date, viewer selector, extractor mode selector, and section navigation.
- Primary `Run Full Demo` CTA plus collapsed manual controls for 10am, 12pm, 2pm, status update, and reset.
- My Todo for selected-viewer assigned work; Manager mode becomes a global priority view.
- Project Boards grouped by project and filterable by All, Only {viewer}, or project.
- Team Review Queue for missing due, unresolved due text, missing assignee, or low confidence.
- Ingestion Run Log with counts and errors.
- Auto-refresh every 3 seconds using vanilla JS fetch.
- Selected-viewer assigned tasks are highlighted tastefully; mention-only notifications stay visible without becoming personal todos.

## Due and Status Rules

The fixture base time is `2025-05-16T09:00:00`, configurable through `DEMO_BASE_DATETIME`.

The demo uses 2025-05-16 as the fixture base date because the provided screenshot contains deadlines such as Monday 5/19 and Tuesday 5/20, which align with the 2025 calendar. This keeps relative date parsing internally consistent with the source data.

本 demo 使用 2025-05-16 作为截图基准日期，因为附件截图中包含 Monday 5/19 和 Tuesday 5/20，这两个日期与 2025 年日历一致。这样可以保证相对时间解析和原始测试数据内部一致。

The main dashboard shows the simulation date, not the real local runtime. Real local execution timestamps are kept in ingestion logs only.

Supported due phrases include:

- 今天 / today
- 这周 / 本周 / this week / 周五前
- 下周一
- 3 天内 / 3天内
- 1 周内 / 1周内
- Monday 5/19
- Tuesday 5/20

Unresolved phrases such as `开盘前`, `day of`, and missing due dates are marked `needs_review=true`.

Done keywords include `已发`, `done`, `已完成`, `sent`, and `published`.

The status update stage is demo-only. It marks five existing tasks done for Chris, Henry, Tara.L, Iris, and 阿可 without creating new tasks.

## Known Limitations

- The deterministic parser is fixture-focused rather than a broad Chinese task parser.
- Screenshot OCR is not implemented in default mode; screenshots are used by optional LLM vision mode.
- Assignment and project inference are intentionally conservative.
- The dashboard is local-only and has no authentication.

## Future Improvements & Production Path

This repo is intentionally a self-contained local demo. The current dashboard is intentionally lightweight: FastAPI + Jinja2 + SQLite + vanilla JavaScript/CSS. Production work would focus on the following areas:

1. **Context-aware extraction**: improve multi-bullet parsing, resolve references such as `这些 / 这几个 / 上面这些`, distinguish broadcast notifications from real task assignments, and improve project, owner, due-date, and status extraction.
2. **More polished commercial dashboard**: keep the local-first architecture lightweight, but consider a professional UI component system or design system to improve visual consistency, interaction quality, and business-facing polish.
3. **Role-based UX optimization**: make Manager view focus on global projects, risk, review queues, and completion status; make personal views focus on individual todos, deadlines, and completed work.
4. **More task status detection**: expand status flow from `todo` to `in_progress`, `blocked`, and `done`, using phrases such as `开始做了`, `卡住了`, `等素材`, `已发`, `done`, `sent`, and `published`.
5. **Human-in-the-loop editing**: allow users to correct assignees, due dates, project, title, and status; approve or reject AI-extracted tasks; and sync confirmed edits back to storage or downstream task systems.
6. **Stronger evidence layer**: add field-level source explanations, crop screenshots to the exact message bubble when OCR/vision bounding boxes are available, and explain why the AI assigned a task to a person.
7. **Closed-loop learning / memory / skills**: learn from reviewer corrections, long-term project ownership patterns, and reusable extraction skills to reduce `needs_review` over time while keeping human review for uncertain cases.
8. **Permission and real user system**: add login, role permissions, Manager / individual / admin access levels, default personal task views, and global Manager oversight.
9. **Notifications and reminders**: send reminders for today’s todos, upcoming due dates, `needs_review` queues, and status changes through channels such as WeCom, email, or Slack.
10. **Real WeChat / WeCom integration**: prefer official WeCom / Enterprise WeChat APIs for stable sender, timestamp, and group metadata. If only regular WeChat is available, use a semi-automated screenshot/OCR adapter with human review. Avoid unofficial hooks, reverse engineering, or reading private WeChat databases due to stability, privacy, and account-safety risks.
