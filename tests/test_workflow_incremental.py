import json
import sqlite3

from agent.storage import Storage
from agent.dedupe import message_hash
from agent.models import ExtractedTask
from agent.normalizer import normalize_task
from agent.workflow import AgentWorkflow


def count_tasks(db_path):
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    finally:
        conn.close()


def test_incremental_ingest_does_not_duplicate_cumulative_snapshots(tmp_path):
    db_path = tmp_path / "tasks.db"
    workflow = AgentWorkflow(Storage(db_path))

    first = workflow.ingest("10am")
    second = workflow.ingest("12pm")
    third = workflow.ingest("2pm")

    assert first.new_tasks_count == 5
    assert second.new_tasks_count == 6
    assert third.new_tasks_count == 6
    assert count_tasks(db_path) == 17

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT COUNT(*), MAX(description), MAX(due_at), MAX(last_seen_snapshot) FROM tasks WHERE canonical_key = ?",
            ("solene|main-visual-poster-first-version",),
        ).fetchone()
        assert rows[0] == 1
        assert "one hero image" in rows[1]
        assert rows[2] == "2025-05-19T18:00"
        assert rows[3] == "2pm"
    finally:
        conn.close()


def test_multitask_message_mentions_stay_task_scoped(tmp_path):
    db_path = tmp_path / "tasks.db"
    storage = Storage(db_path)
    workflow = AgentWorkflow(storage)
    workflow.ingest("10am")

    conn = sqlite3.connect(db_path)
    try:
        rows = {
            row[0]: {
                "assignees": json.loads(row[1]),
                "mentions": json.loads(row[2]),
            }
            for row in conn.execute(
                """
                SELECT canonical_key, assignees_json, mentioned_users_json
                FROM tasks
                WHERE canonical_key IN (?, ?, ?)
                """,
                (
                    "solene|main-visual-poster-first-version",
                    "belmont|yoyo-jason-youtube-video",
                    "verona|photo-first-version",
                ),
            )
        }
    finally:
        conn.close()

    assert "Henry" not in rows["solene|main-visual-poster-first-version"]["mentions"]
    assert "Henry" not in rows["belmont|yoyo-jason-youtube-video"]["mentions"]
    assert "Henry" in rows["verona|photo-first-version"]["mentions"]
    assert "Henry" in rows["verona|photo-first-version"]["assignees"]

    tasks = {task["canonical_key"]: task for task in storage.dashboard_data()["tasks"]}
    assert "Henry" not in tasks["solene|main-visual-poster-first-version"]["viewer_roles"]
    assert "Henry" not in tasks["belmont|yoyo-jason-youtube-video"]["viewer_roles"]
    assert "Henry" in tasks["verona|photo-first-version"]["viewer_roles"]
    henry_related = {key for key, task in tasks.items() if "Henry" in task["viewer_roles"]}
    assert henry_related == {"verona|photo-first-version"}


def test_done_update_marks_belmont_task_done(tmp_path):
    db_path = tmp_path / "tasks.db"
    workflow = AgentWorkflow(Storage(db_path))
    workflow.ingest("10am")
    workflow.ingest("12pm")
    workflow.ingest("2pm")
    done_run = workflow.ingest("done_update")

    conn = sqlite3.connect(db_path)
    try:
        rows = dict(conn.execute("SELECT canonical_key, status FROM tasks").fetchall())
        assert rows["belmont|yoyo-jason-youtube-video"] == "done"
        assert rows["verona|photo-first-version"] == "done"
        assert rows["belmont|broker-folder-social-ads-video-update"] == "done"
        assert rows["social-content|yesterday-event-social-publishing"] == "done"
        assert rows["1847-hudson-blvd|arrival-map-address-description"] == "done"
        assert count_tasks(db_path) == 17
        assert done_run.new_tasks_count == 0
        assert done_run.updated_tasks_count == 5
    finally:
        conn.close()


def test_llm_vision_variants_merge_to_fixture_identities(tmp_path):
    db_path = tmp_path / "tasks.db"
    storage = Storage(db_path)
    variants = [
        ExtractedTask(
            project="General Marketing",
            title="Post yesterday's event content to social channels",
            description="Post yesterday's event content to WeChat Moments, LinkedIn, and Instagram; choose attractive images.",
            assignees=["Iris", "阿可"],
            mentioned_users=["Iris", "阿可"],
            due_text="今天",
            source_message_time="上午 09:42",
            raw_text="@Iris 小秘书 昨天活动的内容今天发朋友圈 +LinkedIn+Ins 配图记得选好看的 @阿可 你那边也帮忙看一眼",
        ),
        ExtractedTask(
            project="Social Media",
            title="Review yesterday event social post images",
            description="Review the images/content for yesterday's event social posts.",
            assignees=["阿可"],
            mentioned_users=["阿可"],
            due_text="今天",
            source_message_time="上午 09:42",
            raw_text="@Iris 小秘书 昨天活动的内容今天发朋友圈 +LinkedIn+Ins 配图记得选好看的 @阿可 你那边也帮忙看一眼",
        ),
        ExtractedTask(
            project="Solene",
            title="Finalize main key visual poster layout",
            description="Finalize the main key visual poster layout: one main image with property, selling points, and price, plus one information graphic with map and features.",
            assignees=[],
            mentioned_users=[],
            due_text="3 天内",
            source_message_time="下午 12:09",
            raw_text="【Solene】3 天内完成主视觉海报首版：一张主图（楼盘+卖点+价格） + 一张信息图（map + features）",
        ),
        ExtractedTask(
            project="1847 HUDSON BLVD",
            title="Create and update correct arrival directions",
            description="Create a correct arrival directions map and mark address input method and route.",
            assignees=["阿可"],
            mentioned_users=["阿可"],
            due_text="下周一",
            source_message_time="上午 10:08",
            raw_text="【1847 Hudson Blvd】下周一跟进：制作正确到达指引地图，并在该楼所有 description 与官网中明确标注正确输入地址方式、正确到达路线 @阿可",
        ),
        ExtractedTask(
            project="1847 Hudson Blvd",
            title="Update official website description",
            description="Do not forget to update the official website description together with the arrival directions updates.",
            assignees=[],
            mentioned_users=[],
            due_text=None,
            source_message_time="下午 12:09",
            raw_text="【1847 Hudson Blvd】再补一条 官网 description 别忘了一起改",
        ),
        ExtractedTask(
            project="Belmont",
            title="Update broker folder with surrounding-area video and coordinate publishing",
            description="Ensure the surrounding-area video is updated into the broker folder and coordinate company publishing and ads.",
            assignees=["Tara.L"],
            mentioned_users=["Tara.L"],
            source_message_time="下午 12:09",
            raw_text="【Belmont】确保周边视频更新进 broker folder，并同步公司发布 Ins、小红书与广告团队推进 @Tara.L",
        ),
        ExtractedTask(
            project="Belmont",
            title="Update neighborhood videos in broker folder and coordinate publishing",
            description="Ensure neighborhood videos are updated into the broker folder and coordinate Instagram, Xiaohongshu, and advertising.",
            assignees=["Tara.L"],
            mentioned_users=["Tara.L"],
            source_message_time="下午 12:09",
            raw_text="【Belmont】确保周边视频更新进 broker folder，并同步公司发布 Ins、小红书与广告团队推进 @Tara.L",
        ),
        ExtractedTask(
            project="Verona",
            title="Deliver Verona photos before video and room tour",
            description="Prioritize Verona photos first due to tight timing, then work on company video and room tour later.",
            assignees=["Henry"],
            mentioned_users=["Henry"],
            due_text="下周有空",
            source_message_time="下午 12:09",
            raw_text="@Henry 时间比较紧凑的话 Verona 就只要照片先，然后再做公司的视频，最后下周有空在做 room tour",
        ),
        ExtractedTask(
            project="Year-End Summit",
            title="Prepare final .pptx and .pdf backup",
            description="Prepare the final .pptx and .pdf backup materials.",
            assignees=["阿可", "Henry", "Iris", "Tara.L", "Chris"],
            mentioned_users=["阿可", "Henry", "Iris", "Tara.L", "Chris"],
            due_text="by Monday 5/19",
            source_message_time="下午 2:02",
            raw_text="【Year-end Summit】给大家同步一下这次年会物料 deadline:\n• Final .pptx + .pdf backup — by Monday 5/19",
        ),
    ]

    for index, extracted in enumerate(variants):
        raw_hash = message_hash(extracted.source_message_time, "Coco-某地产", f"{extracted.raw_text}\nvariant:{index}")
        storage.upsert_task(normalize_task(extracted, raw_hash, "llm_vision_test"))

    tasks = {task["canonical_key"]: task for task in storage.dashboard_data()["tasks"]}

    assert len(tasks) == 6
    assert "social-content|yesterday-event-social-publishing" in tasks
    assert "1847-hudson-blvd|arrival-map-address-description" in tasks
    assert "belmont|broker-folder-social-ads-video-update" in tasks
    assert "verona|photo-first-version" in tasks
    assert "year-end-summit|final-pptx-pdf-backup" in tasks
    assert tasks["year-end-summit|final-pptx-pdf-backup"]["assignees"] == []
    assert set(tasks["year-end-summit|final-pptx-pdf-backup"]["viewer_roles"]) == {"阿可", "Henry", "Iris", "Tara.L", "Chris"}
    assert tasks["solene|main-visual-poster-first-version"]["title_zh"] == "主视觉海报首版"
    assert tasks["belmont|broker-folder-social-ads-video-update"]["title_zh"] == "周边视频更新与社媒/广告同步"
    assert tasks["1847-hudson-blvd|arrival-map-address-description"]["title_zh"] == "到达地图、正确地址与官网描述更新"
    assert tasks["social-content|yesterday-event-social-publishing"]["description_zh"].startswith("将昨日活动内容发布到")
