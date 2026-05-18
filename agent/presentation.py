from __future__ import annotations

from datetime import datetime
from typing import Any

from agent.dedupe import slugify


FIXTURE_DATE = "2025-05-16"
FIXTURE_WEEKDAY_EN = "Friday"
FIXTURE_WEEKDAY_ZH = "周五"
CURRENT_USER = "阿可"
MANAGER_VIEWER = "manager"
VIEWER_ROLES = ["阿可", "Henry", "Iris", "Tara.L", "Chris"]

SCREENSHOT_BY_SNAPSHOT = {
    "10am": "wechat_10am.png",
    "12pm": "wechat_12pm.png",
    "2pm": "wechat_2pm.png",
}

TASK_TRANSLATIONS = {
    "social-content|yesterday-event-social-publishing": {
        "title_zh": "昨日活动内容社媒发布",
        "description_zh": "将昨日活动内容发布到朋友圈、LinkedIn 和 Instagram，并选择好看的配图。",
    },
    "solene|main-visual-poster-first-version": {
        "title_zh": "主视觉海报首版",
        "description_zh": "制作一张主图（楼盘、卖点、价格）和一张信息图（地图、features），并确认是否适合朋友圈/群传播。",
    },
    "solene|ai-teaser-video": {
        "title_zh": "AI teaser 视频",
        "description_zh": "制作 Coming soon 视频和 30 秒项目视频，并确认是否具备社媒传播能力。",
    },
    "solene|pr-release": {
        "title_zh": "PR 发布",
        "description_zh": "主动联系媒体，准备中英文 press release，并确认是否存在免费曝光渠道。",
    },
    "solene|navigation-arrival-guide": {
        "title_zh": "导航与到达指引",
        "description_zh": "整理 driving 路线、地铁路线、周边 landmark，确保第一次来的人也能顺利到达。",
    },
    "solene|broker-email-campaign": {
        "title_zh": "Broker Email Campaign",
        "description_zh": "完成 broker 版 / buyer 版邮件，至少储备 4 期内容，并确认 broker list 和 schedule 是否就绪。",
    },
    "belmont|yoyo-jason-youtube-video": {
        "title_zh": "Yoyo + Jason YouTube 视频发布",
        "description_zh": "将 Yoyo + Jason 视频发布到 YouTube，并为 Chris 提供 YouTube 操作支持。",
    },
    "belmont|broker-folder-social-ads-video-update": {
        "title_zh": "周边视频更新与社媒/广告同步",
        "description_zh": "将周边视频更新进 broker folder，并同步公司 Ins、小红书与广告团队推进。",
    },
    "verona|photo-first-version": {
        "title_zh": "照片首版",
        "description_zh": "优先交付 Verona 照片首版，再推进后续视频工作。",
    },
    "verona|company-video-room-tour-later": {
        "title_zh": "公司视频与 room tour 后续拍摄",
        "description_zh": "照片完成后再做公司视频；家具和时间合适后再安排 room tour。",
    },
    "1847-hudson-blvd|arrival-map-address-description": {
        "title_zh": "到达地图、正确地址与官网描述更新",
        "description_zh": "制作正确到达指引地图，并更新 description 与官网中的正确地址输入方式和到达路线。",
    },
    "company-blog-agent-front-desk|district-intro-copy": {
        "title_zh": "地区介绍文案加入 agent 前台与官网 blog",
        "description_zh": "将公司地区介绍文案加入 agent 前台，并提高公司网站 blog 部分权重。",
    },
    "year-end-summit|final-pptx-pdf-backup": {
        "title_zh": "最终 pptx/pdf 备份",
        "description_zh": "准备最终 .pptx 与 .pdf backup。",
    },
    "year-end-summit|2025-recap-video": {
        "title_zh": "2025 recap 视频",
        "description_zh": "导出 2025 recap video，格式为 .mp4 / H.264。",
    },
    "year-end-summit|music-files": {
        "title_zh": "音乐文件本地下载",
        "description_zh": "将音乐文件下载到本地，格式为 .mp3 或 .m4a。",
    },
    "year-end-summit|final-timed-run-of-show": {
        "title_zh": "最终带 cue 的 timed run-of-show",
        "description_zh": "完成带 cue 的最终 timed run-of-show。",
    },
    "admin-task-ops|sync-all-tasks-to-task-table": {
        "title_zh": "同步 Year-end Summit 年会物料任务进任务表",
        "description_zh": "将 Year-end Summit 年会物料 deadline 同步进任务表，包括 Final .pptx/.pdf backup、2025 recap video、music files 和 final timed run-of-show，确保不要遗漏。",
    },
}


def add_task_presentation_fields(task: dict) -> None:
    translation = TASK_TRANSLATIONS.get(task["canonical_key"], {})
    task["title_en"] = task["title"]
    task["title_zh"] = translation.get("title_zh", task["title"])
    task["description_en"] = task["description"] or ""
    task["description_zh"] = translation.get("description_zh", task["description"] or "")
    task["project_anchor"] = f"project-{slugify(task['project'])}"
    task["project_filter"] = slugify(task["project"])
    task["evidence_screenshot_id"] = evidence_screenshot_id_for(task)
    task["is_demo_only_update"] = task.get("last_seen_snapshot") == "done_update"
    task["review_reasons"] = review_reasons(task)
    task["is_current_user_related"] = is_current_user_related(task)
    task["viewer_match_reasons"] = viewer_match_reasons(task)
    task["viewer_roles"] = list(task["viewer_match_reasons"].keys())
    task["viewer_action_roles"] = actionable_viewer_roles(task)
    task["due_resolved_label"] = task["due_at"][:16].replace("T", " ") if task.get("due_at") else ""
    task["due_needs_review"] = bool(task.get("due_text") and not task.get("due_at")) or not task.get("due_text")
    task["evidence_payload"] = evidence_payload(task)


def is_current_user_related(task: dict) -> bool:
    return any(person_matches_viewer(person, CURRENT_USER) for person in task.get("assignees", []))


def actionable_viewer_roles(task: dict) -> list[str]:
    assignees = task.get("assignees", [])
    return [viewer for viewer in VIEWER_ROLES if any(person_matches_viewer(person, viewer) for person in assignees)]


def viewer_match_reasons(task: dict) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {}
    assignees = task.get("assignees", [])
    mentions = task.get("mentioned_users", [])

    for viewer in VIEWER_ROLES:
        reasons: list[str] = []
        if any(person_matches_viewer(person, viewer) for person in assignees):
            reasons.append("assignee")
        if any(person_matches_viewer(person, viewer) for person in mentions):
            reasons.append("mention")
        if viewer == "阿可" and task.get("is_self"):
            reasons.append("self_alias")
        if reasons:
            matches[viewer] = list(dict.fromkeys(reasons))
    return matches


def person_matches_viewer(person: str, viewer: str) -> bool:
    if person == viewer:
        return True
    if viewer == "Chris" and person.lower() == "mkt chris":
        return True
    return False


def review_reasons(task: dict) -> list[str]:
    reasons: list[str] = []
    due_text = task.get("due_text") or ""
    due_at = task.get("due_at")

    if not task.get("assignees"):
        reasons.append("missing_assignee")
    if not due_text:
        reasons.append("missing_due")
    if due_text and not due_at:
        reasons.append("unresolved_due")
    if any(token in due_text.lower() for token in ["开盘前", "day of", "下周有空", "有空"]):
        reasons.append("ambiguous_timing")
    if float(task.get("confidence") or 0) < 0.75:
        reasons.append("low_confidence")
    if task.get("is_demo_only_update"):
        reasons.append("demo_only_status_update")

    return list(dict.fromkeys(reasons))


def screenshot_id_for(snapshot_id: str | None) -> str | None:
    if snapshot_id in SCREENSHOT_BY_SNAPSHOT:
        return snapshot_id
    return None


def evidence_screenshot_id_for(task: dict) -> str | None:
    # Prefer the latest real screenshot-backed evidence; demo-only status updates have text but no image.
    for message in reversed(task.get("evidence_messages", [])):
        screenshot_id = screenshot_id_for(message.get("snapshot_id"))
        if screenshot_id:
            return screenshot_id
    return screenshot_id_for(task.get("last_seen_snapshot")) or screenshot_id_for(task.get("first_seen_snapshot"))


def fixture_metadata(extractor_mode: str) -> dict[str, str]:
    return {
        "fixture_date": FIXTURE_DATE,
        "fixture_weekday_en": FIXTURE_WEEKDAY_EN,
        "fixture_weekday_zh": FIXTURE_WEEKDAY_ZH,
        "current_user": CURRENT_USER,
        "extractor_mode": extractor_mode,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def timeline_steps(completed_snapshots: set[str], current_snapshot: str | None) -> list[dict[str, Any]]:
    steps = [
        {"snapshot": "10am", "label_en": "10am", "label_zh": "10am"},
        {"snapshot": "12pm", "label_en": "12pm", "label_zh": "12pm"},
        {"snapshot": "2pm", "label_en": "2pm", "label_zh": "2pm"},
        {"snapshot": "done_update", "label_en": "Status update", "label_zh": "状态更新"},
    ]
    for step in steps:
        step["completed"] = step["snapshot"] in completed_snapshots
        step["current"] = step["snapshot"] == current_snapshot
    return steps


def evidence_payload(task: dict) -> dict[str, Any]:
    screenshot_id = task.get("evidence_screenshot_id")
    return {
        "canonical_key": task["canonical_key"],
        "project": task["project"],
        "title_en": task["title_en"],
        "title_zh": task["title_zh"],
        "raw_messages": task.get("evidence_messages", []),
        "screenshot_url": f"/evidence/screenshot/{screenshot_id}" if screenshot_id else None,
        "text_only": not screenshot_id,
        "is_demo_only_update": task.get("is_demo_only_update", False),
        "fields": {
            "canonical_key": task["canonical_key"],
            "due_text": task.get("due_text") or "—",
            "due_at": task.get("due_at") or "—",
            "source_message_time": task.get("source_message_time") or "—",
            "first_seen_snapshot": task.get("first_seen_snapshot") or "—",
            "last_seen_snapshot": task.get("last_seen_snapshot") or "—",
            "source_hash_count": len(task.get("raw_message_hashes", [])),
            "assignees": ", ".join(task.get("assignees", [])) or "—",
            "mentioned_users": ", ".join(task.get("mentioned_users", [])) or "—",
            "confidence": f"{float(task.get('confidence') or 0) * 100:.0f}%",
        },
        "viewer_match_reasons": task.get("viewer_match_reasons", {}),
    }
