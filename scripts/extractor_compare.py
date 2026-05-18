from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.env import load_local_env
from agent.storage import Storage
from agent.workflow import AgentWorkflow
from scripts.demo_qa import EXPECTED_CANONICAL_KEYS, SNAPSHOTS


REPORT_PATH = ROOT / "reports" / "extractor_compare_report.json"
PERSON_VIEWERS = ["阿可", "Henry", "Iris", "Tara.L", "Chris"]
ALLOWED_MODES = {"llm_text", "llm_vision"}


def run_extractor_compare(mode: str, report_path: Path = REPORT_PATH) -> dict[str, Any]:
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode must be one of: {', '.join(sorted(ALLOWED_MODES))}")
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "mode": mode,
            "status": "skipped",
            "reason": "OPENAI_API_KEY is not set",
        }

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        baseline = _run_sequence(tmp_path / "baseline.db", "text_fixture")
        candidate = _run_sequence(tmp_path / "candidate.db", mode)

    report = {
        "mode": mode,
        "model": os.getenv("OPENAI_MODEL", "gpt-5.5"),
        "status": "success",
        "baseline": baseline,
        "candidate": candidate,
        "comparison": _compare(baseline, candidate),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _run_sequence(db_path: Path, mode: str) -> dict[str, Any]:
    storage = Storage(db_path)
    storage.reset()
    workflow = AgentWorkflow(storage)
    runs = []
    for snapshot in SNAPSHOTS:
        snapshot_mode = "text_fixture" if snapshot == "done_update" else mode
        runs.append(workflow.ingest(snapshot, extractor_mode=snapshot_mode).model_dump())
    dashboard = storage.dashboard_data()
    tasks = dashboard["tasks"]
    canonical_keys = sorted(task["canonical_key"] for task in tasks)
    return {
        "total_tasks": len(tasks),
        "canonical_keys": canonical_keys,
        "missing_expected_canonical_keys": sorted(set(EXPECTED_CANONICAL_KEYS) - set(canonical_keys)),
        "extra_canonical_keys": sorted(set(canonical_keys) - set(EXPECTED_CANONICAL_KEYS)),
        "task_count_by_project": dict(sorted(Counter(task["project"] for task in tasks).items())),
        "status_count": dict(sorted(Counter(task["status"] for task in tasks).items())),
        "role_action_keys": _role_keys(tasks, "viewer_action_roles"),
        "role_mention_keys": _role_keys(tasks, "viewer_roles"),
        "localized_text_by_key": _localized_text_by_key(tasks),
        "runs": runs,
    }


def _role_keys(tasks: list[dict[str, Any]], field: str) -> dict[str, list[str]]:
    return {
        viewer: sorted(task["canonical_key"] for task in tasks if viewer in task.get(field, []))
        for viewer in PERSON_VIEWERS
    }


def _compare(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_keys = set(baseline["canonical_keys"])
    candidate_keys = set(candidate["canonical_keys"])
    return {
        "total_tasks_match": baseline["total_tasks"] == candidate["total_tasks"],
        "canonical_keys_match": baseline["canonical_keys"] == candidate["canonical_keys"],
        "missing_from_candidate": sorted(baseline_keys - candidate_keys),
        "extra_in_candidate": sorted(candidate_keys - baseline_keys),
        "project_counts_match": baseline["task_count_by_project"] == candidate["task_count_by_project"],
        "status_counts_match": baseline["status_count"] == candidate["status_count"],
        "zh_display_text_match": baseline["localized_text_by_key"] == candidate["localized_text_by_key"],
        "zh_display_text_diffs": _localized_text_diffs(baseline["localized_text_by_key"], candidate["localized_text_by_key"]),
        "role_action_diffs": _role_diffs(baseline["role_action_keys"], candidate["role_action_keys"]),
        "role_mention_diffs": _role_diffs(baseline["role_mention_keys"], candidate["role_mention_keys"]),
    }


def _role_diffs(baseline: dict[str, list[str]], candidate: dict[str, list[str]]) -> dict[str, dict[str, list[str]]]:
    diffs: dict[str, dict[str, list[str]]] = {}
    for viewer in PERSON_VIEWERS:
        expected = set(baseline.get(viewer, []))
        actual = set(candidate.get(viewer, []))
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing or extra:
            diffs[viewer] = {"missing": missing, "extra": extra}
    return diffs


def _localized_text_by_key(tasks: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    return {
        task["canonical_key"]: {
            "title_zh": task.get("title_zh", ""),
            "description_zh": task.get("description_zh", ""),
        }
        for task in tasks
    }


def _localized_text_diffs(
    baseline: dict[str, dict[str, str]],
    candidate: dict[str, dict[str, str]],
) -> dict[str, dict[str, dict[str, str]]]:
    diffs: dict[str, dict[str, dict[str, str]]] = {}
    for key in sorted(set(baseline) | set(candidate)):
        expected = baseline.get(key)
        actual = candidate.get(key)
        if expected != actual:
            diffs[key] = {"expected": expected or {}, "actual": actual or {}}
    return diffs


def main() -> None:
    load_local_env()
    parser = argparse.ArgumentParser(description="Compare optional LLM extraction against the deterministic text fixture baseline.")
    parser.add_argument("--mode", choices=sorted(ALLOWED_MODES), default=os.getenv("LLM_COMPARE_MODE", "llm_vision"))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    args = parser.parse_args()
    report = run_extractor_compare(args.mode, Path(args.report_path))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
