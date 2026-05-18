from __future__ import annotations

import re
from pathlib import Path

from agent.extractor_base import Extractor
from agent.models import ExtractedTask, ExtractionResult, RawMessage
from agent.normalizer import detect_status, extract_task_mentions


class TextFixtureExtractor(Extractor):
    mode = "text_fixture"

    def extract(self, snapshot_id: str, text_path: Path, image_path: Path | None = None) -> ExtractionResult:
        # STEP 1 - 读取输入快照 / Load input snapshot
        content = text_path.read_text(encoding="utf-8")
        messages = parse_fixture_messages(content)

        # STEP 2 - 结构化抽取 / Structured extraction
        tasks: list[ExtractedTask] = []
        previous_task_message: RawMessage | None = None
        for message in messages:
            message_tasks = extract_tasks_from_message(message, previous_task_message)
            if message_tasks:
                previous_task_message = message
            tasks.extend(message_tasks)

        return ExtractionResult(
            snapshot_id=snapshot_id,
            messages=messages,
            tasks=tasks,
            extractor_mode=self.mode,
        )


def parse_fixture_messages(content: str) -> list[RawMessage]:
    messages: list[RawMessage] = []
    current_time: str | None = None
    current_sender = "Coco-某地产"
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer, current_time, current_sender
        if current_time and buffer:
            raw_text = "\n".join(line.rstrip() for line in buffer).strip()
            if raw_text:
                messages.append(RawMessage(source_time=current_time, sender=current_sender, raw_text=raw_text))
        buffer = []

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        header = re.match(r"^###\s+(.+)$", line)
        if header:
            flush()
            current_time = header.group(1).strip()
            current_sender = "Coco-某地产"
            continue
        if line.startswith("sender:"):
            current_sender = line.split(":", 1)[1].strip() or current_sender
            continue
        if line.strip() == "---":
            flush()
            current_time = None
            continue
        if current_time is not None:
            buffer.append(line)
    flush()
    return messages


def numbered_items(text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        if current:
            items.append(" ".join(part.strip() for part in current if part.strip()))
        current = []

    for line in text.splitlines():
        match = re.match(r"^\s*\d+[\.\、]\s*(.+)$", line.strip())
        if match:
            flush()
            current = [match.group(1)]
        elif current and line.strip():
            current.append(line.strip())

    flush()
    return items


def item_containing(items: list[str], token: str) -> str:
    token_lower = token.lower()
    return next((item for item in items if token_lower in item.lower()), "")


def references_previous_task_context(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    reference_tokens = ["这些", "这几个", "以上", "上面这些", "这些都"]
    admin_intent_tokens = ["同步进我们的任务表", "任务表", "千万不要漏"]
    return any(token in compact for token in reference_tokens) and any(token in compact for token in admin_intent_tokens)


def admin_sync_fields(context_message: RawMessage | None) -> tuple[str, str, list[str]]:
    if context_message and "Year-end Summit" in context_message.raw_text:
        return (
            "Sync Year-end Summit material deadlines into task table",
            (
                "Sync the Year-end Summit material deadlines into the shared task table, including "
                "Final .pptx/.pdf backup, 2025 recap video, music files, and final timed run-of-show. "
                "Make sure nothing is missed."
            ),
            [context_message.raw_text],
        )
    return (
        "Sync listed tasks into task table",
        "Sync all listed work items into the shared task table and make sure nothing is missed.",
        [],
    )


def task(
    message: RawMessage,
    project: str,
    title: str,
    description: str,
    due_text: str | None = None,
    assignees: list[str] | None = None,
    confidence: float = 0.9,
    status: str | None = None,
    source_text: str | None = None,
    mentioned_users: list[str] | None = None,
    context_raw_texts: list[str] | None = None,
) -> ExtractedTask:
    raw = message.raw_text
    mention_source = source_text or raw
    return ExtractedTask(
        project=project,
        title=title,
        description=description,
        due_text=due_text,
        assignees=assignees or [],
        mentioned_users=mentioned_users if mentioned_users is not None else extract_task_mentions(mention_source),
        context_raw_texts=context_raw_texts or [],
        source_message_time=message.source_time,
        raw_text=raw,
        confidence=confidence,
        status=status or detect_status(mention_source),
    )


def extract_tasks_from_message(message: RawMessage, previous_task_message: RawMessage | None = None) -> list[ExtractedTask]:
    text = message.raw_text
    compact = re.sub(r"\s+", " ", text)
    tasks: list[ExtractedTask] = []

    if "早上好" in text and "Solene" in text and "Belmont" in text:
        items = numbered_items(text)
        solene_source = item_containing(items, "Solene")
        belmont_source = item_containing(items, "Belmont")
        verona_source = item_containing(items, "Verona")
        tasks.append(task(
            message,
            "Solene",
            "Main visual poster first version",
            "Complete first version of main visual poster.",
            "这周",
            confidence=0.88,
            source_text=solene_source,
        ))
        tasks.append(task(
            message,
            "Belmont",
            "Yoyo + Jason YouTube video",
            "Publish the Yoyo + Jason video to YouTube.",
            "周五前",
            confidence=0.9,
            source_text=belmont_source,
        ))
        tasks.append(task(
            message,
            "Verona",
            "Photo first version",
            "Provide a first version of Verona photos.",
            "这周",
            assignees=["Henry"],
            confidence=0.86,
            source_text=verona_source,
        ))
        return tasks

    if "昨天活动的内容今天发朋友圈" in compact:
        tasks.append(task(
            message,
            "Social Content",
            "Yesterday event social publishing",
            "Publish yesterday event content to WeChat Moments, LinkedIn and Instagram; choose polished visuals.",
            "今天",
            assignees=["Iris", "阿可"],
            confidence=0.82,
        ))
        return tasks

    if "昨天活动内容" in compact and "朋友圈" in compact and "LinkedIn" in compact and "Ins" in compact:
        tasks.append(task(
            message,
            "Social Content",
            "Yesterday event social publishing",
            "Publish yesterday event content to WeChat Moments, LinkedIn and Instagram; choose polished visuals.",
            "今天" if "今天" in text else None,
            assignees=["Iris"],
            confidence=0.86,
        ))
        return tasks

    if "1847 Hudson Blvd" in text:
        description = "Create arrival guide map and update all descriptions and official website with correct address entry and arrival route."
        if "再补一条" in text:
            description = "Also update official website description together with the arrival/address guidance."
        tasks.append(task(
            message,
            "1847 Hudson Blvd",
            "Arrival guide map, address description and website update",
            description,
            "下周一" if "下周一" in text else None,
            assignees=["阿可"] if "@阿可" in text else [],
            confidence=0.9,
        ))
        return tasks

    if "Solene" in text:
        if "AI teaser" in text:
            tasks.append(task(message, "Solene", "AI teaser video", "Create Coming soon video and 30-second project video; confirm social distribution potential.", "1 周内", confidence=0.93))
        elif "主视觉海报首版" in text:
            tasks.append(task(message, "Solene", "Main visual poster first version", "Create one hero image with building, selling points and price, plus one info map/features image; confirm shareability.", "3 天内", confidence=0.95))
        elif "PR 发布" in text:
            tasks.append(task(message, "Solene", "PR release", "Contact media, prepare Chinese and English press release, and identify free exposure channels.", "开盘前", confidence=0.84))
        elif "导航与到达指引" in text:
            tasks.append(task(message, "Solene", "Navigation and arrival guide", "Prepare driving route, subway route and nearby landmark guidance so first-time visitors can arrive easily.", "本周", confidence=0.92))
        elif "Broker Email Campaign" in text:
            tasks.append(task(message, "Solene", "Broker Email Campaign", "Create broker and buyer email versions, prepare at least four issues, and confirm broker list and schedule.", "本周", confidence=0.93))
        return tasks

    if "Verona" in text and "照片先" in text:
        tasks.append(task(message, "Verona", "Photo first version", "Prioritize Verona photo delivery before video work.", None, assignees=["Henry"], confidence=0.82))
        tasks.append(task(message, "Verona", "Company video and room tour later", "Do company video after photos, then room tour when furniture and timing are ready.", "下周有空", assignees=["Henry"], confidence=0.68))
        return tasks

    if "Verona" in text and "照片首版" in text:
        tasks.append(task(message, "Verona", "Photo first version", "Provide a first version of Verona photos.", None, assignees=["Henry"], confidence=0.88))
        return tasks

    if "Belmont" in text and "Yoyo + Jason" in text:
        tasks.append(task(
            message,
            "Belmont",
            "Yoyo + Jason YouTube video",
            "Publish the Yoyo + Jason video to YouTube; Chris needs support on the YouTube workflow.",
            "周五前" if "周五前" in text else None,
            assignees=["mkt Chris"] if "@mkt Chris" in text else ["Chris"] if "Chris" in text else [],
            confidence=0.91,
        ))
        return tasks

    if "Belmont" in text and "broker folder" in text:
        tasks.append(task(
            message,
            "Belmont",
            "Surrounding-area video update and distribution",
            "Update surrounding-area video into broker folder and coordinate company Instagram, Xiaohongshu and ads distribution.",
            None,
            assignees=["Tara.L"] if "@Tara.L" in text else [],
            confidence=0.88,
        ))
        return tasks

    if "公司地区介绍" in text and "agent 前台" in text:
        tasks.append(task(
            message,
            "Company Blog / Agent Front Desk",
            "Add district intro copy to agent front desk and website blog",
            "Add company district introduction copy to the agent front desk for Guangzhou and increase company website blog weight.",
            None,
            assignees=["阿可"] if "@阿可" in text else [],
            confidence=0.83,
        ))
        return tasks

    if "Year-end Summit" in text:
        bullet_specs = [
            ("Final pptx and pdf backup", "Final .pptx and .pdf backup.", "Monday 5/19", 0.94),
            ("2025 recap video", "2025 recap video exported as .mp4, H.264.", "Monday 5/19", 0.94),
            ("Music files", "Download music files locally as .mp3/.m4a.", "day of", 0.78),
            ("Final timed run-of-show with cues", "Final timed run-of-show with cues.", "Tuesday 5/20", 0.94),
        ]
        for title, description, due, confidence in bullet_specs:
            tasks.append(task(message, "Year-end Summit", title, description, due, confidence=confidence))
        return tasks

    if "同步进我们的任务表" in text:
        context_message = previous_task_message if references_previous_task_context(text) else None
        title, description, context_raw_texts = admin_sync_fields(context_message)
        tasks.append(task(
            message,
            "Admin / Task Ops",
            title,
            description,
            None,
            assignees=["阿可", "Iris"],
            mentioned_users=["阿可", "Iris"],
            context_raw_texts=context_raw_texts,
            confidence=0.86,
        ))
        return tasks

    return tasks
