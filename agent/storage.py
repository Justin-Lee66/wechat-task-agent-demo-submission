from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from agent.env import load_local_env
from agent.models import NormalizedTask
from agent.presentation import CURRENT_USER, add_task_presentation_fields, fixture_metadata, timeline_steps


load_local_env()

DEFAULT_DB_PATH = Path("data/tasks.db")


def utc_now() -> str:
    return datetime.now(UTC).replace(tzinfo=None).isoformat(timespec="seconds")


class Storage:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or os.getenv("DATABASE_PATH", DEFAULT_DB_PATH))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)

    def reset(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                DROP TABLE IF EXISTS task_events;
                DROP TABLE IF EXISTS tasks;
                DROP TABLE IF EXISTS messages;
                DROP TABLE IF EXISTS ingestion_runs;
                """
            )
            conn.executescript(SCHEMA_SQL)

    def start_run(self, snapshot_id: str, extractor_mode: str) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO ingestion_runs (snapshot_id, extractor_mode, status, started_at)
                VALUES (?, ?, 'running', ?)
                """,
                (snapshot_id, extractor_mode, utc_now()),
            )
            return int(cur.lastrowid)

    def complete_run(
        self,
        run_id: int,
        status: str,
        new_messages_count: int,
        new_tasks_count: int,
        updated_tasks_count: int,
        error_message: str | None = None,
        extractor_mode: str | None = None,
    ) -> None:
        with self.connect() as conn:
            if extractor_mode:
                conn.execute("UPDATE ingestion_runs SET extractor_mode = ? WHERE id = ?", (extractor_mode, run_id))
            conn.execute(
                """
                UPDATE ingestion_runs
                SET status = ?, completed_at = ?, error_message = ?,
                    new_messages_count = ?, new_tasks_count = ?, updated_tasks_count = ?
                WHERE id = ?
                """,
                (status, utc_now(), error_message, new_messages_count, new_tasks_count, updated_tasks_count, run_id),
            )

    def insert_message(self, snapshot_id: str, source_time: str, sender: str, raw_text: str, raw_hash: str) -> bool:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO messages (snapshot_id, source_time, sender, raw_text, raw_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (snapshot_id, source_time, sender, raw_text, raw_hash, utc_now()),
            )
            return cur.rowcount > 0

    def upsert_task(self, task: NormalizedTask) -> str:
        with self.connect() as conn:
            existing = conn.execute("SELECT * FROM tasks WHERE canonical_key = ?", (task.canonical_key,)).fetchone()
            if not existing:
                conn.execute(
                    """
                    INSERT INTO tasks (
                        canonical_key, project, title, description, assignees_json, mentioned_users_json,
                        due_text, due_at, due_confidence, status, is_self, source_message_time,
                        first_seen_snapshot, last_seen_snapshot, raw_message_hashes_json, needs_review,
                        confidence, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task.canonical_key,
                        task.project,
                        task.title,
                        task.description,
                        json.dumps(task.assignees, ensure_ascii=False),
                        json.dumps(task.mentioned_users, ensure_ascii=False),
                        task.due_text,
                        task.due_at.isoformat(timespec="minutes") if task.due_at else None,
                        task.due_confidence,
                        task.status,
                        int(task.is_self),
                        task.source_message_time,
                        task.first_seen_snapshot,
                        task.last_seen_snapshot,
                        json.dumps(list(dict.fromkeys([*task.context_raw_hashes, task.raw_message_hash])), ensure_ascii=False),
                        int(task.needs_review),
                        task.confidence,
                        utc_now(),
                        utc_now(),
                    ),
                )
                self._event(conn, task.canonical_key, "created", {"snapshot_id": task.last_seen_snapshot})
                return "created"

            merged, meaningful_change = self._merge(existing, task)
            conn.execute(
                """
                UPDATE tasks
                SET project = ?, title = ?, description = ?, assignees_json = ?, mentioned_users_json = ?,
                    due_text = ?, due_at = ?, due_confidence = ?, status = ?, is_self = ?,
                    source_message_time = ?, last_seen_snapshot = ?, raw_message_hashes_json = ?,
                    needs_review = ?, confidence = ?, updated_at = ?
                WHERE canonical_key = ?
                """,
                (
                    merged["project"],
                    merged["title"],
                    merged["description"],
                    json.dumps(merged["assignees"], ensure_ascii=False),
                    json.dumps(merged["mentioned_users"], ensure_ascii=False),
                    merged["due_text"],
                    merged["due_at"],
                    merged["due_confidence"],
                    merged["status"],
                    int(merged["is_self"]),
                    merged["source_message_time"],
                    task.last_seen_snapshot,
                    json.dumps(merged["raw_hashes"], ensure_ascii=False),
                    int(merged["needs_review"]),
                    merged["confidence"],
                    utc_now(),
                    task.canonical_key,
                ),
            )
            if meaningful_change:
                self._event(conn, task.canonical_key, "updated", {"snapshot_id": task.last_seen_snapshot, "status": merged["status"]})
                return "updated"
            return "seen"

    def _merge(self, existing: sqlite3.Row, task: NormalizedTask) -> tuple[dict[str, Any], bool]:
        old_assignees = json.loads(existing["assignees_json"] or "[]")
        old_mentions = json.loads(existing["mentioned_users_json"] or "[]")
        old_hashes = json.loads(existing["raw_message_hashes_json"] or "[]")
        assignees = list(dict.fromkeys([*old_assignees, *task.assignees]))
        mentions = list(dict.fromkeys([*old_mentions, *task.mentioned_users]))
        raw_hashes = list(dict.fromkeys([*old_hashes, *task.context_raw_hashes, task.raw_message_hash]))

        description = existing["description"] or ""
        if len(task.description or "") > len(description):
            description = task.description

        due_text = existing["due_text"]
        due_at = existing["due_at"]
        due_confidence = float(existing["due_confidence"] or 0)
        if task.due_at and (not due_at or task.due_confidence >= due_confidence or len(task.description) > len(existing["description"] or "")):
            due_text = task.due_text
            due_at = task.due_at.isoformat(timespec="minutes")
            due_confidence = task.due_confidence

        status = "done" if existing["status"] == "done" or task.status == "done" else task.status or existing["status"]
        confidence = max(float(existing["confidence"] or 0), task.confidence)
        needs_review = bool(existing["needs_review"]) or task.needs_review
        if due_at and assignees and confidence >= 0.75:
            needs_review = False
        if "开盘前" in (due_text or "").lower() or "day of" in (due_text or "").lower() or "下周有空" in (due_text or ""):
            needs_review = True

        merged = {
            "project": existing["project"],
            "title": existing["title"],
            "description": description,
            "assignees": assignees,
            "mentioned_users": mentions,
            "due_text": due_text,
            "due_at": due_at,
            "due_confidence": due_confidence,
            "status": status,
            "is_self": bool(existing["is_self"]) or task.is_self,
            "source_message_time": task.source_message_time or existing["source_message_time"],
            "raw_hashes": raw_hashes,
            "needs_review": needs_review,
            "confidence": confidence,
        }
        meaningful_change = any(
            [
                description != (existing["description"] or ""),
                due_at != existing["due_at"],
                status != existing["status"],
                assignees != old_assignees,
                mentions != old_mentions,
                bool(merged["is_self"]) != bool(existing["is_self"]),
                bool(merged["needs_review"]) != bool(existing["needs_review"]),
            ]
        )
        return merged, meaningful_change

    def _event(self, conn: sqlite3.Connection, canonical_key: str, event_type: str, payload: dict[str, Any]) -> None:
        row = conn.execute("SELECT id FROM tasks WHERE canonical_key = ?", (canonical_key,)).fetchone()
        if not row:
            return
        conn.execute(
            "INSERT INTO task_events (task_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)",
            (row["id"], event_type, json.dumps(payload, ensure_ascii=False), utc_now()),
        )

    def dashboard_data(self) -> dict[str, Any]:
        with self.connect() as conn:
            tasks = [dict(row) for row in conn.execute("SELECT * FROM tasks ORDER BY project, due_at IS NULL, due_at, title")]
            runs = [dict(row) for row in conn.execute("SELECT * FROM ingestion_runs ORDER BY id DESC LIMIT 12")]
            raw_hashes: list[str] = []
            for row in tasks:
                raw_hashes.extend(json.loads(row["raw_message_hashes_json"] or "[]"))
            message_by_hash = self._messages_by_hash(conn, raw_hashes)

        for row in tasks:
            row["assignees"] = json.loads(row.pop("assignees_json") or "[]")
            row["mentioned_users"] = json.loads(row.pop("mentioned_users_json") or "[]")
            row["raw_message_hashes"] = json.loads(row.pop("raw_message_hashes_json") or "[]")
            row["evidence_messages"] = [message_by_hash[raw_hash] for raw_hash in row["raw_message_hashes"] if raw_hash in message_by_hash]
            row["is_self"] = bool(row["is_self"])
            row["needs_review"] = bool(row["needs_review"])
            row["due_label"] = row["due_at"][:16].replace("T", " ") if row["due_at"] else (row["due_text"] or "Needs review")
            add_task_presentation_fields(row)

        today_prefix = os.getenv("DEMO_BASE_DATETIME", "2025-05-16T09:00:00")[:10]
        active = [task for task in tasks if task["status"] != "done"]
        today_todo = [task for task in active if task["due_at"] and task["due_at"].startswith(today_prefix)]
        today_todo.extend([task for task in active if task["due_at"] and task["due_at"] < today_prefix])
        today_todo.sort(key=lambda item: item["due_at"] or "9999")
        priority_todo = list(tasks)
        priority_todo.sort(key=self._priority_sort_key)
        due_today_keys = {task["canonical_key"] for task in today_todo}
        for task in tasks:
            task["is_due_today"] = task["canonical_key"] in due_today_keys

        my_todo = [task for task in tasks if task["is_current_user_related"]]
        my_todo.sort(key=self._my_todo_sort_key)
        needs_review = [task for task in tasks if task["needs_review"]]
        needs_review.sort(key=self._review_sort_key)

        grouped: dict[str, list[dict[str, Any]]] = {}
        for item in tasks:
            grouped.setdefault(item["project"], []).append(item)

        successful_runs = [run for run in runs if run["status"] == "success"]
        current_snapshot = successful_runs[0]["snapshot_id"] if successful_runs else None
        completed_snapshots = {run["snapshot_id"] for run in successful_runs}
        extractor_mode = runs[0]["extractor_mode"] if runs else os.getenv("EXTRACTOR_MODE", "text_fixture")
        metadata = fixture_metadata(extractor_mode)
        metadata["current_snapshot"] = current_snapshot or "none"
        kpis = {
            "total": len(tasks),
            "due_today": len(today_todo),
            "me": len(my_todo),
            "needs_review": sum(1 for task in tasks if task["needs_review"]),
            "done": sum(1 for task in tasks if task["status"] == "done"),
        }
        return {
            "tasks": tasks,
            "project_groups": grouped,
            "my_todo": my_todo,
            "priority_todo": priority_todo,
            "today_todo": today_todo,
            "needs_review": needs_review,
            "runs": runs,
            "kpis": kpis,
            "metadata": metadata,
            "timeline_steps": timeline_steps(completed_snapshots, current_snapshot),
        }

    def _my_todo_sort_key(self, task: dict[str, Any]) -> tuple[int, str, str]:
        explicit_assignee = CURRENT_USER in task.get("assignees", [])
        if task.get("due_at"):
            bucket = 0
            due_sort = task["due_at"]
        elif explicit_assignee:
            bucket = 1
            due_sort = "9998"
        else:
            bucket = 2
            due_sort = "9999"
        return (bucket, due_sort, task.get("source_message_time") or "")

    def _priority_sort_key(self, task: dict[str, Any]) -> tuple[int, str, str]:
        if task.get("due_at"):
            return (0, task["due_at"], task.get("source_message_time") or "")
        return (1, "9999", task.get("source_message_time") or "")

    def _review_sort_key(self, task: dict[str, Any]) -> tuple[int, str]:
        reasons = set(task.get("review_reasons", []))
        if reasons & {"unresolved_due", "missing_due", "ambiguous_timing"}:
            severity = 0
        elif "low_confidence" in reasons:
            severity = 1
        elif "missing_assignee" in reasons:
            severity = 2
        else:
            severity = 3
        return (severity, task.get("source_message_time") or "")

    def qa_summary_counts(self) -> dict[str, Any]:
        with self.connect() as conn:
            total_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            done_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'").fetchone()[0]
            duplicates = [
                row["canonical_key"]
                for row in conn.execute(
                    "SELECT canonical_key FROM tasks GROUP BY canonical_key HAVING COUNT(*) > 1 ORDER BY canonical_key"
                )
            ]
        return {"total_tasks": total_tasks, "done_tasks": done_tasks, "duplicate_canonical_keys": duplicates}

    def _messages_by_hash(self, conn: sqlite3.Connection, raw_hashes: list[str]) -> dict[str, dict[str, Any]]:
        if not raw_hashes:
            return {}
        placeholders = ",".join("?" for _ in raw_hashes)
        rows = conn.execute(
            f"""
            SELECT snapshot_id, source_time, sender, raw_text, raw_hash
            FROM messages
            WHERE raw_hash IN ({placeholders})
            """,
            raw_hashes,
        ).fetchall()
        return {row["raw_hash"]: dict(row) for row in rows}


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ingestion_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  snapshot_id TEXT NOT NULL,
  extractor_mode TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TEXT NOT NULL,
  completed_at TEXT,
  error_message TEXT,
  new_messages_count INTEGER DEFAULT 0,
  new_tasks_count INTEGER DEFAULT 0,
  updated_tasks_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  snapshot_id TEXT NOT NULL,
  source_time TEXT,
  sender TEXT,
  raw_text TEXT NOT NULL,
  raw_hash TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  canonical_key TEXT NOT NULL UNIQUE,
  project TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  assignees_json TEXT NOT NULL,
  mentioned_users_json TEXT NOT NULL,
  due_text TEXT,
  due_at TEXT,
  due_confidence REAL DEFAULT 0,
  status TEXT NOT NULL,
  is_self INTEGER DEFAULT 0,
  source_message_time TEXT,
  first_seen_snapshot TEXT,
  last_seen_snapshot TEXT,
  raw_message_hashes_json TEXT NOT NULL,
  needs_review INTEGER DEFAULT 0,
  confidence REAL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS task_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(task_id) REFERENCES tasks(id)
);
"""
