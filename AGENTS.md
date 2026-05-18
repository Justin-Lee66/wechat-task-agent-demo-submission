# AGENTS.md

Project-level coding memory for `wechat-task-agent-demo`.

## Product Stance

- Build a self-contained local demo from fixtures.
- Do not implement real WeChat hooks, private database reads, reverse engineering, or unofficial automation.
- Keep default demo mode API-key-free.
- Mention Hermes only as a future production extension, never as a dependency.

## Implementation Preferences

- Python FastAPI + SQLite + Jinja2.
- Pydantic models define extraction schemas.
- Vanilla JS polling for dashboard refresh.
- Keep files small and named by workflow responsibility.
- Use bilingual comments only for major workflow steps.

## Demo Base Time

Use `DEMO_BASE_DATETIME=2025-05-16T09:00:00` unless a reviewer overrides it.

## Dedupe Rules

- Message dedupe: unique `raw_message_hash`.
- Task dedupe: `project_slug|canonical_title_slug`.
- Later, richer messages should update existing tasks instead of creating duplicates.

## Safety

Secrets stay in `.env`, never committed.
The app should always run with `EXTRACTOR_MODE=text_fixture` and no secrets.

## Documentation Sync Rules

- If dashboard UX changes, update README Demo UX and Dashboard Features.
- If fixtures change, update README Verification, tests, and QA expected output.
- If role/viewer logic changes, update README and docs/UI_AUDIT.md.
- If status keyword demo changes, update data/text_fallback, tests, QA report, and README.
- If LLM extraction, prompts, or smoke tests change, update README, docs/PROMPT_DESIGN.md, and docs/LLM_SMOKE_TEST.md.
- Keep README reviewer-facing and concise.
- Do not include internal chat instructions, iterative prompts, or messy development notes in final-facing docs.

## ChatGPT Connector Handoff

Every completed development pass should end with these five handoff fields so ChatGPT can review the GitHub repo or PR consistently:

1. Git branch name
2. Commit SHA
3. Files changed
4. Test result
5. QA report output

Keep the handoff concise and pasteable into ChatGPT.
