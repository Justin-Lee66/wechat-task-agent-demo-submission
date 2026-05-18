# Prompt Design

The optional LLM extractor uses `agent/prompts.py`.

Core prompt rules:

- Extract only actionable work items.
- Preserve original due phrases in `due_text`.
- Do not invent absolute due dates.
- Allow one message to produce multiple tasks.
- Capture bracketed project names and `@mentions`.
- Use the fixture's canonical project/task taxonomy so cumulative screenshots merge into stable task identities.
- Scope mentions to the specific bullet or sentence that produced the task. A mention in one bullet must not be inherited by sibling tasks in the same raw message.
- Treat `大家` / `给大家同步一下` as broadcast visibility, not assignment.
- Resolve unambiguous follow-up pronouns such as `这些`, `这几个`, `以上`, and `上面这些` against the immediately previous task-bearing message. If the follow-up assigns admin/sync work, create a standalone Admin / Task Ops task enriched with the previous context. If the follow-up only adds details to a prior task, merge it as a task update.
- For `@阿可 @Iris ... 这些都同步进我们的任务表`, create or enrich the standalone Admin / Task Ops task and put the previous Year-end Summit deadline list in `context_raw_texts`. Do not assign the Year-end Summit production tasks themselves to 阿可/Iris unless explicitly stated.
- Leave missing assignee/due empty for downstream review flags.
- Return strict JSON only.

The app does not blindly trust model output. The LLM extractor uses the OpenAI Responses API with Pydantic structured output (`ExtractionResult`), retries failures, and falls back to deterministic text fixtures.

After schema validation, LLM outputs pass through the same normalization and dedupe layer as `text_fixture`. This layer maps common vision/text wording variants back to the standard task keys, for example:

- `General Marketing` / `Social Media` -> `Social Content`
- `Company Website / Agent Portal` -> `Company Blog / Agent Front Desk`
- `Update official website description` under 1847 Hudson Blvd -> `1847-hudson-blvd|arrival-map-address-description`
- `Deliver Verona photos before video and room tour` -> `verona|photo-first-version`

This keeps the optional LLM path useful without allowing free-form model wording to break incremental task merging.
