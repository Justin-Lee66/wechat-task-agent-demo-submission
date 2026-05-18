from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from agent.env import load_local_env
from agent.extractor_llm import LLMExtractor
from agent.extractor_text_fixture import TextFixtureExtractor
from agent.models import ExtractionResult


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "llm_smoke_report.json"
TEXT_FIXTURES = ROOT / "data" / "text_fallback"
SCREENSHOTS = ROOT / "data" / "screenshots"
SCREENSHOT_BY_SNAPSHOT = {
    "10am": SCREENSHOTS / "wechat_10am.png",
    "12pm": SCREENSHOTS / "wechat_12pm.png",
    "2pm": SCREENSHOTS / "wechat_2pm.png",
}
ALLOWED_MODES = {"llm_text", "llm_vision"}


def main(argv: list[str] | None = None) -> None:
    load_local_env()
    parser = argparse.ArgumentParser(description="Run an optional live LLM extraction smoke test.")
    parser.add_argument("--mode", choices=sorted(ALLOWED_MODES), default=None, help="LLM extractor mode to test.")
    parser.add_argument("--snapshot-id", default=os.getenv("LLM_SMOKE_SNAPSHOT", "10am"), help="Fixture snapshot id.")
    parser.add_argument("--report-path", default=str(REPORT_PATH), help="Smoke report output path.")
    args = parser.parse_args(argv)

    if not os.getenv("OPENAI_API_KEY"):
        print("llm-smoke skipped: OPENAI_API_KEY is not set.")
        return

    report = run_llm_smoke(args.snapshot_id, _selected_mode(args.mode), Path(args.report_path))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


def run_llm_smoke(snapshot_id: str, mode: str, report_path: Path = REPORT_PATH) -> dict[str, Any]:
    text_path = TEXT_FIXTURES / f"{snapshot_id}.txt"
    image_path = SCREENSHOT_BY_SNAPSHOT.get(snapshot_id)
    if mode == "llm_vision" and image_path is None:
        raise RuntimeError(f"llm_vision smoke only supports screenshots for: {', '.join(SCREENSHOT_BY_SNAPSHOT)}")

    error_message: str | None = None
    fallback_used = False
    try:
        result = LLMExtractor(mode).extract(snapshot_id, text_path, image_path)
    except Exception as exc:  # pragma: no cover - requires optional live API path
        error_message = _sanitize_error(str(exc))
        fallback_used = True
        result = TextFixtureExtractor().extract(snapshot_id, text_path, image_path)

    schema_valid = isinstance(result, ExtractionResult)
    report = {
        "provider": "openai",
        "mode": mode,
        "model": os.getenv("OPENAI_MODEL", "gpt-5.5"),
        "snapshot_id": snapshot_id,
        "status": "fallback" if fallback_used else "success",
        "extracted_task_count": len(result.tasks),
        "schema_valid": schema_valid,
        "fallback_used": fallback_used,
        "error_message": error_message,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _selected_mode(cli_mode: str | None) -> str:
    configured = cli_mode or os.getenv("LLM_SMOKE_MODE") or os.getenv("EXTRACTOR_MODE", "")
    return configured if configured in ALLOWED_MODES else "llm_text"


def _sanitize_error(message: str) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if key:
        message = message.replace(key, "[redacted]")
    return re.sub(r"sk-[A-Za-z0-9_-]+", "[redacted]", message)


if __name__ == "__main__":
    main()
