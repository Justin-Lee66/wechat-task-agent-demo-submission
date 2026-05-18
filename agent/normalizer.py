from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from agent.dedupe import canonical_project, canonical_task_key, canonical_title
from agent.models import ExtractedTask, NormalizedTask


DEFAULT_BASE_DATETIME = "2025-05-16T09:00:00"
SELF_ALIASES = ["阿可"]
STATUS_DONE_KEYWORDS = ["已发", "done", "已完成", "sent", "published"]
ROLE_PREFIX_MENTIONS = {"mkt"}
GROUP_BROADCAST_USERS = ["阿可", "Henry", "Iris", "Tara.L", "Chris"]
GROUP_BROADCAST_PATTERNS = [
    r"给大家同步",
    r"跟大家同步",
    r"同步给大家",
]


@dataclass(frozen=True)
class DueParseResult:
    due_at: datetime | None
    confidence: float
    needs_review: bool


def get_base_datetime() -> datetime:
    raw = os.getenv("DEMO_BASE_DATETIME", DEFAULT_BASE_DATETIME)
    return datetime.fromisoformat(raw)


def at_business_close(day: datetime) -> datetime:
    return day.replace(hour=18, minute=0, second=0, microsecond=0)


def next_weekday(base: datetime, weekday: int) -> datetime:
    days_ahead = weekday - base.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return at_business_close(base + timedelta(days=days_ahead))


def parse_due_text(due_text: str | None, base: datetime | None = None) -> DueParseResult:
    base = base or get_base_datetime()
    text = (due_text or "").strip()
    if not text:
        return DueParseResult(None, 0.0, True)

    lowered = text.lower()
    unresolved = ["开盘前", "day of", "下周有空", "有空"]
    if any(token in lowered for token in unresolved):
        return DueParseResult(None, 0.2, True)

    if re.search(r"(今天|today)", lowered):
        return DueParseResult(at_business_close(base), 0.95, False)

    if re.search(r"(这周|本周|this week|周五前)", lowered):
        return DueParseResult(at_business_close(base), 0.9, False)

    if "下周一" in text:
        return DueParseResult(next_weekday(base, 0), 0.95, False)

    match = re.search(r"(\d+)\s*天内", text)
    if match:
        days = int(match.group(1))
        return DueParseResult(at_business_close(base + timedelta(days=days)), 0.9, False)

    match = re.search(r"(\d+)\s*周内", text)
    if match:
        weeks = int(match.group(1))
        return DueParseResult(at_business_close(base + timedelta(days=weeks * 7)), 0.9, False)

    match = re.search(r"monday\s+(\d{1,2})/(\d{1,2})", lowered)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        return DueParseResult(datetime(base.year, month, day, 18, 0), 0.95, False)

    match = re.search(r"tuesday\s+(\d{1,2})/(\d{1,2})", lowered)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        return DueParseResult(datetime(base.year, month, day, 18, 0), 0.95, False)

    return DueParseResult(None, 0.2, True)


def extract_mentions(text: str) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for match in re.finditer(r"@([A-Za-z0-9_.\-\u4e00-\u9fff]+)(?:\s+([A-Za-z][A-Za-z0-9_.-]*))?", text):
        mention = match.group(1)
        role_suffix = match.group(2)
        if mention.lower() in ROLE_PREFIX_MENTIONS and role_suffix:
            mention = f"{mention} {role_suffix}"
        if mention not in seen:
            seen.add(mention)
            ordered.append(mention)
    return ordered


def infer_group_broadcast_mentions(text: str) -> list[str]:
    compact = re.sub(r"\s+", "", text)
    if any(re.search(pattern, compact) for pattern in GROUP_BROADCAST_PATTERNS):
        return list(GROUP_BROADCAST_USERS)
    return []


def extract_task_mentions(text: str) -> list[str]:
    # STEP 2 - 结构化抽取补全 / Add semantic group-broadcast mentions
    return list(dict.fromkeys([*extract_mentions(text), *infer_group_broadcast_mentions(text)]))


def has_self_mention(text: str, mentions: list[str] | None = None) -> bool:
    if mentions is not None:
        return any(alias in mentions for alias in SELF_ALIASES)
    mentions = extract_task_mentions(text)
    return any(alias in mentions or f"@{alias}" in text for alias in SELF_ALIASES)


def detect_status(text: str) -> str:
    lowered = text.lower()
    return "done" if any(keyword.lower() in lowered for keyword in STATUS_DONE_KEYWORDS) else "todo"


def normalize_person_name(name: str, raw_text: str = "") -> str:
    cleaned = re.sub(r"^@+", "", name.strip())
    cleaned = re.sub(r"\s+", " ", cleaned)
    lowered = cleaned.lower()
    raw_lowered = raw_text.lower()

    if lowered in {"ake", "阿可"}:
        return "阿可"
    if lowered in {"iris", "iris 小秘书", "小秘书"}:
        return "Iris"
    if lowered in {"henry"}:
        return "Henry"
    if lowered in {"tara", "tara.l", "taral"}:
        return "Tara.L"
    if lowered in {"mkt chris", "mkt-chris", "mkt_chris"}:
        return "mkt Chris"
    if lowered == "chris":
        return "mkt Chris" if re.search(r"@?mkt\s+chris", raw_lowered) else "Chris"
    if lowered == "mkt" and "chris" in raw_lowered:
        return "mkt Chris"
    return cleaned


def normalize_people(names: list[str], raw_text: str = "") -> list[str]:
    normalized: list[str] = []
    for name in names:
        person = normalize_person_name(name, raw_text)
        if not person or person.lower() == "mkt":
            continue
        normalized.append(person)
    return list(dict.fromkeys(normalized))


def remove_broadcast_only_assignees(project: str, assignees: list[str], raw_text: str) -> list[str]:
    if project != "Year-end Summit":
        return assignees
    if not infer_group_broadcast_mentions(raw_text):
        return assignees
    compact = re.sub(r"\s+", "", raw_text)
    if "@" in compact:
        return assignees
    return [person for person in assignees if person not in GROUP_BROADCAST_USERS and person != "mkt Chris"]


def normalize_task(
    task: ExtractedTask,
    raw_message_hash: str,
    snapshot_id: str,
    context_raw_hashes: list[str] | None = None,
) -> NormalizedTask:
    # STEP 3 - 归一化字段 / Normalize extracted fields
    raw_text = task.raw_text or task.description or task.title
    project = canonical_project(task.project, task.title, task.description, raw_text)
    title = canonical_title(project, task.title, task.description, raw_text)
    assignees = normalize_people(task.assignees, raw_text)
    assignees = remove_broadcast_only_assignees(project, assignees, raw_text)
    explicit_mentions = normalize_people(task.mentioned_users, raw_text)
    mentions = list(dict.fromkeys([*explicit_mentions, *infer_group_broadcast_mentions(raw_text)]))
    due = parse_due_text(task.due_text)
    status = "done" if task.status == "done" or detect_status(raw_text) == "done" else "todo"
    needs_review = (
        due.needs_review
        or not assignees
        or task.confidence < 0.75
    )
    data = task.model_dump()
    data["project"] = project
    data["title"] = title
    data["assignees"] = assignees
    data["mentioned_users"] = mentions
    data["status"] = status
    return NormalizedTask(
        **data,
        canonical_key=canonical_task_key(project, title, task.description, raw_text),
        due_at=due.due_at,
        due_confidence=due.confidence,
        needs_review=needs_review,
        is_self=has_self_mention(raw_text, mentions),
        raw_message_hash=raw_message_hash,
        context_raw_hashes=context_raw_hashes or [],
        first_seen_snapshot=snapshot_id,
        last_seen_snapshot=snapshot_id,
    )
