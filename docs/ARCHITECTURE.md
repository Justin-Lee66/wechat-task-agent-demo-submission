# Architecture

```text
data/text_fallback + data/screenshots
        |
        v
agent.workflow.AgentWorkflow
        |
        +-- TextFixtureExtractor
        +-- optional LLMExtractor
        |
        v
agent.normalizer
        |
        v
agent.storage.Storage
        |
        v
FastAPI routes + Jinja2 partials + static/app.js polling
```

The workflow is intentionally linear so a reviewer can trace a task from source message to dashboard row.

## Key Modules

- `agent/models.py`: Pydantic extraction and ingestion schemas.
- `agent/extractor_text_fixture.py`: deterministic fixture extraction.
- `agent/extractor_llm.py`: optional OpenAI text/vision extractor with fallback support.
- `agent/normalizer.py`: due parsing, status detection, mention and self detection.
- `agent/dedupe.py`: raw message hashes and canonical task keys.
- `agent/storage.py`: SQLite schema, task merge/upsert, dashboard queries.
- `app/routes.py`: page, partial, ingest, and reset routes.

