from scripts.demo_qa import EXPECTED_CANONICAL_KEYS, run_demo_qa


def test_demo_qa_report_contract(tmp_path):
    report = run_demo_qa(
        db_path=tmp_path / "tasks.db",
        report_path=tmp_path / "demo_qa_report.json",
    )

    assert report["duplicate_canonical_keys"] == []
    assert set(EXPECTED_CANONICAL_KEYS).issubset(set(report["all_canonical_keys"]))
    assert report["missing_expected_canonical_keys"] == []
    assert report["belmont_youtube_done_after_update"] is True
    assert report["ake_completion_done"] is True
    assert report["henry_completion_done"] is True
    assert report["iris_completion_done"] is True
    assert report["tara_completion_done"] is True
    assert report["chris_completion_done"] is True
    assert report["admin_task_preserved"] is True
    assert report["admin_task_context_enriched"] is True
    assert report["admin_task_evidence_has_year_end_context"] is True
    assert report["admin_task_evidence_has_sync_message"] is True
    assert report["admin_task_evidence_message_count"] == 2
    assert report["admin_task_assignees_mentions_correct"] is True
    assert report["solene_main_visual_merged_into_one_task"] is True
    assert report["hudson_blvd_description_map_merged_into_one_task"] is True
    assert report["total_tasks"] == 17
    assert report["status_count"] == {"done": 5, "todo": 12}
    assert report["self_task_count"] >= 1
    assert report["needs_review_count"] >= 1
    done_update = report["ingestion_runs"][-1]
    assert done_update["snapshot_id"] == "done_update"
    assert done_update["new_tasks_count"] == 0
    assert done_update["updated_tasks_count"] == 5
    assert (tmp_path / "demo_qa_report.json").exists()


def test_merged_tasks_appear_once_only(tmp_path):
    report = run_demo_qa(db_path=tmp_path / "tasks.db", report_path=None, write_report=False)
    keys = report["all_canonical_keys"]

    assert keys.count("solene|main-visual-poster-first-version") == 1
    assert keys.count("1847-hudson-blvd|arrival-map-address-description") == 1
