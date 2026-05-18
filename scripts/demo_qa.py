from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

from agent.storage import DEFAULT_DB_PATH, Storage
from agent.workflow import AgentWorkflow


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_PATH = ROOT / "reports" / "demo_qa_report.json"
SNAPSHOTS = ["10am", "12pm", "2pm", "done_update"]

EXPECTED_CANONICAL_KEYS = [
    "solene|main-visual-poster-first-version",
    "solene|ai-teaser-video",
    "solene|pr-release",
    "solene|navigation-arrival-guide",
    "solene|broker-email-campaign",
    "belmont|yoyo-jason-youtube-video",
    "belmont|broker-folder-social-ads-video-update",
    "verona|photo-first-version",
    "verona|company-video-room-tour-later",
    "1847-hudson-blvd|arrival-map-address-description",
    "social-content|yesterday-event-social-publishing",
    "company-blog-agent-front-desk|district-intro-copy",
    "year-end-summit|final-pptx-pdf-backup",
    "year-end-summit|2025-recap-video",
    "year-end-summit|music-files",
    "year-end-summit|final-timed-run-of-show",
    "admin-task-ops|sync-all-tasks-to-task-table",
]

ROLE_COMPLETION_KEYS = {
    "ake_completion_done": "1847-hudson-blvd|arrival-map-address-description",
    "henry_completion_done": "verona|photo-first-version",
    "iris_completion_done": "social-content|yesterday-event-social-publishing",
    "tara_completion_done": "belmont|broker-folder-social-ads-video-update",
    "chris_completion_done": "belmont|yoyo-jason-youtube-video",
}


def run_demo_qa(
    db_path: str | Path | None = None,
    report_path: str | Path | None = DEFAULT_REPORT_PATH,
    write_report: bool = True,
) -> dict[str, Any]:
    storage = Storage(db_path or DEFAULT_DB_PATH)
    storage.reset()
    workflow = AgentWorkflow(storage)

    # STEP 1 - 重放演示快照 / Replay deterministic demo snapshots
    run_summaries = [workflow.ingest(snapshot).model_dump() for snapshot in SNAPSHOTS]

    # STEP 2 - 查询验证数据 / Query verification data
    tasks, run_rows, duplicates = _load_rows(storage.db_path)
    canonical_keys = sorted(task["canonical_key"] for task in tasks)
    expected_set = set(EXPECTED_CANONICAL_KEYS)
    actual_set = set(canonical_keys)

    report = {
        "total_tasks": len(tasks),
        "task_count_by_project": dict(sorted(Counter(task["project"] for task in tasks).items())),
        "status_count": dict(sorted(Counter(task["status"] for task in tasks).items())),
        "self_task_count": sum(1 for task in tasks if task["is_self"]),
        "needs_review_count": sum(1 for task in tasks if task["needs_review"]),
        "ingestion_runs": run_summaries,
        "ingestion_runs_from_db": run_rows,
        "all_canonical_keys": canonical_keys,
        "duplicate_canonical_keys": duplicates,
        "missing_expected_canonical_keys": sorted(expected_set - actual_set),
        "belmont_youtube_done_after_update": _status_for(tasks, "belmont|yoyo-jason-youtube-video") == "done",
        **{name: _status_for(tasks, canonical_key) == "done" for name, canonical_key in ROLE_COMPLETION_KEYS.items()},
        **_admin_context_checks(tasks),
        "solene_main_visual_merged_into_one_task": _merged_once(tasks, "solene|main-visual-poster-first-version"),
        "hudson_blvd_description_map_merged_into_one_task": _merged_once(tasks, "1847-hudson-blvd|arrival-map-address-description"),
    }

    if write_report and report_path:
        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return report


def _load_rows(db_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        tasks = [dict(row) for row in conn.execute("SELECT * FROM tasks ORDER BY canonical_key")]
        raw_hashes: list[str] = []
        for task in tasks:
            task["is_self"] = bool(task["is_self"])
            task["needs_review"] = bool(task["needs_review"])
            task["assignees"] = json.loads(task["assignees_json"] or "[]")
            task["mentioned_users"] = json.loads(task["mentioned_users_json"] or "[]")
            task["raw_message_hashes"] = json.loads(task["raw_message_hashes_json"] or "[]")
            raw_hashes.extend(task["raw_message_hashes"])
        placeholders = ",".join("?" for _ in raw_hashes)
        message_by_hash = {}
        if placeholders:
            message_by_hash = {
                row["raw_hash"]: row["raw_text"]
                for row in conn.execute(f"SELECT raw_hash, raw_text FROM messages WHERE raw_hash IN ({placeholders})", raw_hashes)
            }
        for task in tasks:
            task["evidence_texts"] = [message_by_hash[raw_hash] for raw_hash in task["raw_message_hashes"] if raw_hash in message_by_hash]
        runs = [
            dict(row)
            for row in conn.execute(
                """
                SELECT snapshot_id, extractor_mode, status, new_messages_count,
                       new_tasks_count, updated_tasks_count, error_message
                FROM ingestion_runs
                ORDER BY id
                """
            )
        ]
        duplicates = [
            row["canonical_key"]
            for row in conn.execute(
                "SELECT canonical_key FROM tasks GROUP BY canonical_key HAVING COUNT(*) > 1 ORDER BY canonical_key"
            )
        ]
        return tasks, runs, duplicates
    finally:
        conn.close()


def _status_for(tasks: list[dict[str, Any]], canonical_key: str) -> str | None:
    for task in tasks:
        if task["canonical_key"] == canonical_key:
            return task["status"]
    return None


def _task_for(tasks: list[dict[str, Any]], canonical_key: str) -> dict[str, Any] | None:
    return next((task for task in tasks if task["canonical_key"] == canonical_key), None)


def _admin_context_checks(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    task = _task_for(tasks, "admin-task-ops|sync-all-tasks-to-task-table")
    evidence_text = "\n".join(task.get("evidence_texts", [])) if task else ""
    description = task.get("description", "") if task else ""
    return {
        "admin_task_preserved": task is not None,
        "admin_task_context_enriched": bool(
            task
            and "Year-end Summit" in task.get("title", "")
            and "Year-end Summit" in description
            and "Final .pptx" in description
            and "2025 recap video" in description
            and "music files" in description
            and "run-of-show" in description
        ),
        "admin_task_evidence_has_year_end_context": "Year-end Summit" in evidence_text and "Final .pptx + .pdf backup" in evidence_text,
        "admin_task_evidence_has_sync_message": "这些都同步进我们的任务表" in evidence_text,
        "admin_task_evidence_message_count": len(task.get("evidence_texts", [])) if task else 0,
        "admin_task_assignees_mentions_correct": bool(
            task and task.get("assignees") == ["阿可", "Iris"] and task.get("mentioned_users") == ["阿可", "Iris"]
        ),
    }


def _merged_once(tasks: list[dict[str, Any]], canonical_key: str) -> bool:
    matched = [task for task in tasks if task["canonical_key"] == canonical_key]
    return len(matched) == 1 and len(matched[0]["raw_message_hashes"]) >= 2


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic QA for the WeChat task agent demo.")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="SQLite database path.")
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH), help="JSON report output path.")
    args = parser.parse_args()
    report = run_demo_qa(args.db_path, args.report_path)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
