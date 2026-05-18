from __future__ import annotations

import hashlib
import re
import unicodedata


CANONICAL_TITLE_BY_SLUG = {
    "main-visual-poster-first-version": "Main visual poster first version",
    "ai-teaser-video": "AI teaser video",
    "pr-release": "PR release",
    "navigation-arrival-guide": "Navigation and arrival guide",
    "broker-email-campaign": "Broker Email Campaign",
    "yoyo-jason-youtube-video": "Yoyo + Jason YouTube video",
    "broker-folder-social-ads-video-update": "Surrounding-area video update and distribution",
    "photo-first-version": "Photo first version",
    "company-video-room-tour-later": "Company video and room tour later",
    "arrival-map-address-description": "Arrival guide map, address description and website update",
    "district-intro-copy": "Add district intro copy to agent front desk and website blog",
    "final-pptx-pdf-backup": "Final pptx and pdf backup",
    "2025-recap-video": "2025 recap video",
    "music-files": "Music files",
    "final-timed-run-of-show": "Final timed run-of-show with cues",
    "sync-all-tasks-to-task-table": "Sync Year-end Summit material deadlines into task table",
    "yesterday-event-social-publishing": "Yesterday event social publishing",
}

KNOWN_TITLE_SLUGS = {
    "solene:main visual poster first version": "main-visual-poster-first-version",
    "solene:ai teaser video": "ai-teaser-video",
    "solene:pr release": "pr-release",
    "solene:navigation and arrival guide": "navigation-arrival-guide",
    "solene:broker email campaign": "broker-email-campaign",
    "belmont:yoyo + jason youtube video": "yoyo-jason-youtube-video",
    "belmont:surrounding-area video update and distribution": "broker-folder-social-ads-video-update",
    "verona:photo first version": "photo-first-version",
    "verona:company video and room tour later": "company-video-room-tour-later",
    "1847 hudson blvd:arrival guide map, address description and website update": "arrival-map-address-description",
    "company blog / agent front desk:add district intro copy to agent front desk and website blog": "district-intro-copy",
    "year-end summit:final pptx and pdf backup": "final-pptx-pdf-backup",
    "year-end summit:2025 recap video": "2025-recap-video",
    "year-end summit:music files": "music-files",
    "year-end summit:final timed run-of-show with cues": "final-timed-run-of-show",
    "admin / task ops:sync listed tasks into task table": "sync-all-tasks-to-task-table",
    "admin / task ops:sync year-end summit material deadlines into task table": "sync-all-tasks-to-task-table",
    "social content:yesterday event social publishing": "yesterday-event-social-publishing",
}


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def message_hash(source_time: str, sender: str, raw_text: str) -> str:
    normalized = "\n".join(
        [
            normalize_space(source_time),
            normalize_space(sender),
            normalize_space(raw_text),
        ]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    value = value.replace("&", " and ").replace("+", " ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "untitled"


def canonical_project(project: str, title: str = "", description: str = "", raw_text: str = "") -> str:
    """Normalize LLM project-name variants back to the fixture project taxonomy."""
    project_clean = normalize_space(project)
    project_slug = slugify(project_clean)
    exact_project = _canonical_project_from_slug(project_slug)
    if exact_project:
        return exact_project

    combined = _combined_text(project, title, description, raw_text)

    if "1847" in combined and ("hudson" in combined or "哈德逊" in combined):
        return "1847 Hudson Blvd"
    if "year-end summit" in combined or "year end summit" in combined or "年会" in combined:
        return "Year-end Summit"
    if "admin" in project_slug or "task-ops" in project_slug or "任务表" in combined:
        return "Admin / Task Ops"
    if "belmont" in combined:
        return "Belmont"
    if "solene" in combined:
        return "Solene"
    if "verona" in combined:
        return "Verona"
    if _has_any(combined, ["district intro", "regional introduction", "agent portal", "agent front", "company blog", "公司地区介绍", "agent 前台"]):
        return "Company Blog / Agent Front Desk"
    if project_slug in {"social-media", "general-marketing", "social-content"} or _has_any(
        combined,
        ["yesterday", "event content", "social channels", "moments", "linkedin", "instagram", "朋友圈", "昨天活动"],
    ):
        return "Social Content"

    return project_clean or "General"


def canonical_title_slug(project: str, title: str, description: str = "", raw_text: str = "") -> str:
    canonical = canonical_project(project, title, description, raw_text)
    exact = KNOWN_TITLE_SLUGS.get(f"{canonical.lower()}:{title.lower()}") or KNOWN_TITLE_SLUGS.get(f"{project.lower()}:{title.lower()}")
    if exact:
        return exact

    combined = _combined_text(canonical, title, description, raw_text)

    if canonical == "Solene":
        if _has_any(combined, ["broker email", "broker list", "buyer version", "buyer 版", "邮件"]):
            return "broker-email-campaign"
        if _has_any(combined, ["ai teaser", "coming soon", "30-second", "30 秒", "项目视频"]):
            return "ai-teaser-video"
        if _has_any(combined, ["pr release", "press release", "free exposure", "媒体", "曝光", "pr 发布"]):
            return "pr-release"
        if _has_any(combined, ["navigation", "arrival guide", "driving route", "subway", "landmark", "导航", "到达指引"]):
            return "navigation-arrival-guide"
        if _has_any(combined, ["main visual", "key visual", "poster", "hero image", "information graphic", "主视觉", "海报", "主图", "信息图"]):
            return "main-visual-poster-first-version"

    if canonical == "Belmont":
        if _has_any(combined, ["yoyo", "jason", "youtube"]):
            return "yoyo-jason-youtube-video"
        if _has_any(combined, ["broker folder", "surrounding", "neighborhood", "xiao", "xiaohongshu", "广告", "周边视频"]):
            return "broker-folder-social-ads-video-update"

    if canonical == "Verona":
        title_lower = title.lower()
        photo_first = _has_any(combined, ["photo", "photos", "photography", "照片"])
        later_video = _has_any(title_lower, ["company video", "room tour"]) and not _has_any(title_lower, ["photo", "photos", "照片"])
        if later_video:
            return "company-video-room-tour-later"
        if photo_first:
            return "photo-first-version"
        if _has_any(combined, ["room tour", "furniture", "公司视频", "家具"]):
            return "company-video-room-tour-later"

    if canonical == "1847 Hudson Blvd":
        if _has_any(combined, ["arrival", "address", "description", "website", "map", "路线", "地址", "官网", "到达"]):
            return "arrival-map-address-description"

    if canonical == "Company Blog / Agent Front Desk":
        if _has_any(combined, ["district", "regional introduction", "agent", "blog", "地区介绍", "前台"]):
            return "district-intro-copy"

    if canonical == "Year-end Summit":
        if _has_any(combined, ["pptx", "pdf", "backup"]):
            return "final-pptx-pdf-backup"
        if _has_any(combined, ["recap", "h.264", "mp4"]):
            return "2025-recap-video"
        if _has_any(combined, ["music", "mp3", "m4a", "音乐"]):
            return "music-files"
        if _has_any(combined, ["run-of-show", "run of show", "cue", "cues", "流程"]):
            return "final-timed-run-of-show"

    if canonical == "Admin / Task Ops":
        if _has_any(combined, ["task table", "任务表", "sync", "同步", "千万不要漏"]):
            return "sync-all-tasks-to-task-table"

    if canonical == "Social Content":
        if _has_any(combined, ["yesterday", "event content", "social", "moments", "linkedin", "instagram", "images", "昨天活动", "朋友圈", "配图"]):
            return "yesterday-event-social-publishing"

    return slugify(title)


def canonical_title(project: str, title: str, description: str = "", raw_text: str = "") -> str:
    slug = canonical_title_slug(project, title, description, raw_text)
    return CANONICAL_TITLE_BY_SLUG.get(slug, normalize_space(title))


def canonical_task_key(project: str, title: str, description: str = "", raw_text: str = "") -> str:
    canonical = canonical_project(project, title, description, raw_text)
    return f"{slugify(canonical)}|{canonical_title_slug(canonical, title, description, raw_text)}"


def _combined_text(*parts: str) -> str:
    return unicodedata.normalize("NFKC", " ".join(part or "" for part in parts)).lower()


def _has_any(text: str, tokens: list[str]) -> bool:
    return any(token.lower() in text for token in tokens)


def _canonical_project_from_slug(project_slug: str) -> str | None:
    aliases = {
        "1847-hudson-blvd": "1847 Hudson Blvd",
        "1847-hudson": "1847 Hudson Blvd",
        "admin-task-ops": "Admin / Task Ops",
        "admin-ops": "Admin / Task Ops",
        "belmont": "Belmont",
        "company-blog-agent-front-desk": "Company Blog / Agent Front Desk",
        "company-website-agent-portal": "Company Blog / Agent Front Desk",
        "company-website-agent-front-desk": "Company Blog / Agent Front Desk",
        "general-marketing": "Social Content",
        "social-content": "Social Content",
        "social-media": "Social Content",
        "solene": "Solene",
        "verona": "Verona",
        "year-end-summit": "Year-end Summit",
        "year-end": "Year-end Summit",
        "year-end-summit-materials": "Year-end Summit",
    }
    return aliases.get(project_slug)
