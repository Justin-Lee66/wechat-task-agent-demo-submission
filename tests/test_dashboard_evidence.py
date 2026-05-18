from fastapi.testclient import TestClient

from agent.models import IngestionSummary
from agent.storage import Storage
from agent.workflow import AgentWorkflow
import app.routes as routes
from app.main import app


def test_dashboard_data_includes_evidence_and_review_reasons(tmp_path):
    storage = Storage(tmp_path / "tasks.db")
    workflow = AgentWorkflow(storage)
    for snapshot in ["10am", "12pm", "2pm", "done_update"]:
        workflow.ingest(snapshot)

    data = storage.dashboard_data()
    tasks = {task["canonical_key"]: task for task in data["tasks"]}
    my_keys = {task["canonical_key"] for task in data["my_todo"]}

    solene = tasks["solene|main-visual-poster-first-version"]
    assert solene["first_seen_snapshot"] == "10am"
    assert solene["last_seen_snapshot"] == "2pm"
    assert solene["evidence_screenshot_id"] == "12pm"
    assert len(solene["evidence_messages"]) >= 2
    assert solene["title_zh"] == "主视觉海报首版"

    assert all(task["evidence_screenshot_id"] in {"10am", "12pm", "2pm"} for task in tasks.values())
    assert tasks["belmont|yoyo-jason-youtube-video"]["last_seen_snapshot"] == "done_update"
    assert tasks["belmont|yoyo-jason-youtube-video"]["evidence_screenshot_id"] == "12pm"
    assert tasks["belmont|broker-folder-social-ads-video-update"]["evidence_screenshot_id"] == "12pm"
    assert tasks["social-content|yesterday-event-social-publishing"]["evidence_screenshot_id"] == "10am"
    assert tasks["1847-hudson-blvd|arrival-map-address-description"]["evidence_screenshot_id"] == "12pm"

    pr_release = tasks["solene|pr-release"]
    assert "unresolved_due" in pr_release["review_reasons"]
    assert "ambiguous_timing" in pr_release["review_reasons"]

    verona_later = tasks["verona|company-video-room-tour-later"]
    assert "low_confidence" in verona_later["review_reasons"]
    assert "ambiguous_timing" in verona_later["review_reasons"]

    assert my_keys == {
        "1847-hudson-blvd|arrival-map-address-description",
        "admin-task-ops|sync-all-tasks-to-task-table",
        "company-blog-agent-front-desk|district-intro-copy",
        "social-content|yesterday-event-social-publishing",
    }
    assert tasks["belmont|broker-folder-social-ads-video-update"] not in data["my_todo"]
    assert solene["due_text"] == "3 天内"
    assert solene["due_resolved_label"] == "2025-05-19 18:00"

    assert "阿可" in tasks["social-content|yesterday-event-social-publishing"]["viewer_roles"]
    assert "阿可" in tasks["1847-hudson-blvd|arrival-map-address-description"]["viewer_roles"]
    assert "Henry" in tasks["verona|photo-first-version"]["viewer_roles"]
    assert "Henry" in tasks["verona|company-video-room-tour-later"]["viewer_roles"]
    assert "Tara.L" in tasks["belmont|broker-folder-social-ads-video-update"]["viewer_roles"]
    assert "Chris" in tasks["belmont|yoyo-jason-youtube-video"]["viewer_roles"]
    assert "mkt Chris" in tasks["belmont|yoyo-jason-youtube-video"]["assignees"]
    assert "mkt Chris" in tasks["belmont|yoyo-jason-youtube-video"]["mentioned_users"]
    assert "mkt" not in tasks["belmont|yoyo-jason-youtube-video"]["mentioned_users"]
    assert "Iris" in tasks["social-content|yesterday-event-social-publishing"]["viewer_roles"]
    assert "Iris" in tasks["admin-task-ops|sync-all-tasks-to-task-table"]["viewer_roles"]
    assert "manager" not in tasks["social-content|yesterday-event-social-publishing"]["viewer_roles"]

    admin = tasks["admin-task-ops|sync-all-tasks-to-task-table"]
    assert "Year-end Summit" in admin["title_en"]
    assert "Year-end Summit" in admin["description_en"]
    assert "Final .pptx" in admin["description_en"]
    assert "2025 recap video" in admin["description_en"]
    assert "music files" in admin["description_en"]
    assert "run-of-show" in admin["description_en"]
    assert admin["title_zh"] == "同步 Year-end Summit 年会物料任务进任务表"
    assert admin["assignees"] == ["阿可", "Iris"]
    assert admin["mentioned_users"] == ["阿可", "Iris"]
    admin_evidence = "\n".join(message["raw_text"] for message in admin["evidence_messages"])
    assert "Year-end Summit" in admin_evidence
    assert "Final .pptx + .pdf backup" in admin_evidence
    assert "这些都同步进我们的任务表" in admin_evidence
    assert len(admin["evidence_messages"]) == 2

    for key in [
        "year-end-summit|2025-recap-video",
        "year-end-summit|final-pptx-pdf-backup",
        "year-end-summit|final-timed-run-of-show",
        "year-end-summit|music-files",
    ]:
        assert tasks[key]["assignees"] == []
        assert tasks[key]["mentioned_users"] == ["阿可", "Henry", "Iris", "Tara.L", "Chris"]
        assert set(tasks[key]["viewer_roles"]) == {"阿可", "Henry", "Iris", "Tara.L", "Chris"}
        assert tasks[key]["viewer_action_roles"] == []
        assert key not in my_keys
        assert "missing_assignee" in tasks[key]["review_reasons"]


def test_dashboard_routes_expose_summary_and_screenshot():
    client = TestClient(app)

    assert client.get("/").status_code == 200
    assert 'id="viewer-select"' in client.get("/").text
    assert client.get("/api/summary").status_code == 200
    screenshot = client.get("/evidence/screenshot/2pm")
    assert screenshot.status_code == 200
    assert screenshot.headers["content-type"] == "image/png"
    assert client.get("/evidence/screenshot/done_update").status_code == 404


def test_config_endpoint_hides_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("EXTRACTOR_MODE", "text_fixture")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5.5")

    payload = TestClient(app).get("/api/config").json()

    assert payload == {
        "openai_key_configured": False,
        "default_extractor_mode": "text_fixture",
        "allowed_extractor_modes": ["text_fixture", "llm_text", "llm_vision"],
        "openai_model": "gpt-5.5",
    }
    assert "OPENAI_API_KEY" not in payload


def test_ingest_route_validates_and_passes_extractor_mode(monkeypatch):
    captured = {}

    class FakeWorkflow:
        def __init__(self, storage):
            self.storage = storage

        def ingest(self, snapshot_id, extractor_mode=None):
            captured["snapshot_id"] = snapshot_id
            captured["extractor_mode"] = extractor_mode
            return IngestionSummary(
                run_id=1,
                snapshot_id=snapshot_id,
                extractor_mode=extractor_mode or "text_fixture",
                status="success",
            )

    monkeypatch.setattr(routes, "AgentWorkflow", FakeWorkflow)
    monkeypatch.setattr(routes, "get_storage", lambda: object())
    client = TestClient(app)

    response = client.post("/api/ingest/10am?extractor_mode=llm_text")

    assert response.status_code == 200
    assert captured == {"snapshot_id": "10am", "extractor_mode": "llm_text"}
    assert response.json()["extractor_mode"] == "llm_text"
    assert client.post("/api/ingest/10am?extractor_mode=bad_mode").status_code == 400
