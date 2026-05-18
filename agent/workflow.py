from __future__ import annotations

import os
from pathlib import Path

from agent.dedupe import message_hash
from agent.env import load_local_env
from agent.extractor_llm import LLMExtractor
from agent.extractor_text_fixture import TextFixtureExtractor
from agent.models import IngestionSummary
from agent.normalizer import normalize_task
from agent.storage import Storage


load_local_env()

ROOT = Path(__file__).resolve().parents[1]
TEXT_FIXTURES = ROOT / "data" / "text_fallback"
SCREENSHOTS = ROOT / "data" / "screenshots"


class AgentWorkflow:
    def __init__(self, storage: Storage | None = None) -> None:
        self.storage = storage or Storage()

    def ingest(self, snapshot_id: str, extractor_mode: str | None = None) -> IngestionSummary:
        requested_mode = extractor_mode or os.getenv("EXTRACTOR_MODE", "text_fixture")
        run_id = self.storage.start_run(snapshot_id, requested_mode)
        new_messages = 0
        new_tasks = 0
        updated_tasks = 0
        error_message: str | None = None

        try:
            result = self._extract(snapshot_id, requested_mode)

            # STEP 4 - 入库并去重 / Persist with message and task dedupe
            message_hashes_by_text: dict[str, str] = {}
            for message in result.messages:
                raw_hash = message_hash(message.source_time, message.sender, message.raw_text)
                message_hashes_by_text[message.raw_text] = raw_hash
                if self.storage.insert_message(snapshot_id, message.source_time, message.sender, message.raw_text, raw_hash):
                    new_messages += 1

            for extracted in result.tasks:
                raw_hash = message_hashes_by_text.get(extracted.raw_text)
                if not raw_hash:
                    raw_hash = message_hash(extracted.source_message_time, "Coco-某地产", extracted.raw_text)
                context_raw_hashes = [
                    message_hashes_by_text[raw_text]
                    for raw_text in extracted.context_raw_texts
                    if raw_text in message_hashes_by_text
                ]
                normalized = normalize_task(extracted, raw_hash, snapshot_id, context_raw_hashes)
                outcome = self.storage.upsert_task(normalized)
                if outcome == "created":
                    new_tasks += 1
                elif outcome == "updated":
                    updated_tasks += 1

            self.storage.complete_run(run_id, "success", new_messages, new_tasks, updated_tasks, error_message, result.extractor_mode)
            return IngestionSummary(
                run_id=run_id,
                snapshot_id=snapshot_id,
                extractor_mode=result.extractor_mode,
                status="success",
                new_messages_count=new_messages,
                new_tasks_count=new_tasks,
                updated_tasks_count=updated_tasks,
                error_message=error_message,
            )
        except Exception as exc:
            error_message = str(exc)
            self.storage.complete_run(run_id, "failed", new_messages, new_tasks, updated_tasks, error_message)
            return IngestionSummary(
                run_id=run_id,
                snapshot_id=snapshot_id,
                extractor_mode=requested_mode,
                status="failed",
                new_messages_count=new_messages,
                new_tasks_count=new_tasks,
                updated_tasks_count=updated_tasks,
                error_message=error_message,
            )

    def _extract(self, snapshot_id: str, requested_mode: str):
        text_path = TEXT_FIXTURES / f"{snapshot_id}.txt"
        image_name = {
            "10am": "wechat_10am.png",
            "12pm": "wechat_12pm.png",
            "2pm": "wechat_2pm.png",
        }.get(snapshot_id)
        image_path = (SCREENSHOTS / image_name) if image_name else None

        if requested_mode in {"llm_text", "llm_vision"} and os.getenv("OPENAI_API_KEY"):
            try:
                return LLMExtractor(requested_mode).extract(snapshot_id, text_path, image_path)
            except Exception as exc:
                fallback = TextFixtureExtractor().extract(snapshot_id, text_path, image_path)
                fallback.extractor_mode = f"text_fixture_fallback_after_{requested_mode}"
                fallback.errors.append(str(exc))
                return fallback

        return TextFixtureExtractor().extract(snapshot_id, text_path, image_path)
