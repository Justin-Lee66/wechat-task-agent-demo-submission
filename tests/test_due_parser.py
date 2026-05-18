from datetime import datetime

from agent.normalizer import parse_due_text


BASE = datetime.fromisoformat("2025-05-16T09:00:00")


def test_due_parser_relative_phrases():
    assert parse_due_text("今天", BASE).due_at.date().isoformat() == "2025-05-16"
    assert parse_due_text("这周", BASE).due_at.isoformat(timespec="minutes") == "2025-05-16T18:00"
    assert parse_due_text("周五前", BASE).due_at.isoformat(timespec="minutes") == "2025-05-16T18:00"
    assert parse_due_text("下周一", BASE).due_at.isoformat(timespec="minutes") == "2025-05-19T18:00"
    assert parse_due_text("3 天内", BASE).due_at.isoformat(timespec="minutes") == "2025-05-19T18:00"
    assert parse_due_text("1周内", BASE).due_at.isoformat(timespec="minutes") == "2025-05-23T18:00"
    assert parse_due_text("by Monday 5/19", BASE).due_at.isoformat(timespec="minutes") == "2025-05-19T18:00"
    assert parse_due_text("by Tuesday 5/20", BASE).due_at.isoformat(timespec="minutes") == "2025-05-20T18:00"


def test_due_parser_unresolved_phrases():
    assert parse_due_text("开盘前", BASE).needs_review is True
    assert parse_due_text("day of", BASE).due_at is None
    assert parse_due_text(None, BASE).needs_review is True
