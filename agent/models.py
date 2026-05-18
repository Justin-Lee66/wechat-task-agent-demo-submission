from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


TaskStatus = Literal["todo", "in_progress", "done", "blocked"]


class RawMessage(BaseModel):
    source_time: str
    sender: str = "Coco-某地产"
    raw_text: str


class ExtractedTask(BaseModel):
    project: str
    title: str
    description: str = ""
    assignees: list[str] = Field(default_factory=list)
    mentioned_users: list[str] = Field(default_factory=list)
    context_raw_texts: list[str] = Field(default_factory=list)
    due_text: str | None = None
    status: TaskStatus = "todo"
    source_message_time: str = ""
    raw_text: str = ""
    confidence: float = 0.9


class ExtractionResult(BaseModel):
    snapshot_id: str
    messages: list[RawMessage] = Field(default_factory=list)
    tasks: list[ExtractedTask] = Field(default_factory=list)
    extractor_mode: str = "text_fixture"
    errors: list[str] = Field(default_factory=list)


class NormalizedTask(ExtractedTask):
    canonical_key: str
    due_at: datetime | None = None
    due_confidence: float = 0.0
    needs_review: bool = False
    is_self: bool = False
    raw_message_hash: str = ""
    context_raw_hashes: list[str] = Field(default_factory=list)
    first_seen_snapshot: str = ""
    last_seen_snapshot: str = ""


class IngestionSummary(BaseModel):
    run_id: int
    snapshot_id: str
    extractor_mode: str
    status: str
    new_messages_count: int = 0
    new_tasks_count: int = 0
    updated_tasks_count: int = 0
    error_message: str | None = None


def model_to_jsonable(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return model.dict()
