from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any

from agent.extractor_base import Extractor
from agent.models import ExtractionResult
from agent.prompts import SYSTEM_PROMPT


class LLMExtractor(Extractor):
    def __init__(self, mode: str) -> None:
        if mode not in {"llm_text", "llm_vision"}:
            raise ValueError("mode must be llm_text or llm_vision")
        self.mode = mode

    def extract(self, snapshot_id: str, text_path: Path, image_path: Path | None = None) -> ExtractionResult:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set")

        from openai import OpenAI

        client = OpenAI()
        model = os.getenv("OPENAI_MODEL", "gpt-5.5")
        last_error: Exception | None = None

        for attempt in range(3):
            try:
                content = self._build_content(snapshot_id, text_path, image_path)
                response = client.responses.parse(
                    model=model,
                    instructions=SYSTEM_PROMPT,
                    input=content,
                    text_format=ExtractionResult,
                )
                result = response.output_parsed
                if result is None:
                    raise RuntimeError("LLM response did not include parsed structured output")
                result.snapshot_id = result.snapshot_id or snapshot_id
                result.extractor_mode = self.mode
                return result
            except Exception as exc:  # pragma: no cover - optional network path
                last_error = exc
                if attempt == 2:
                    break

        raise RuntimeError(f"LLM extraction failed after retries: {last_error}")

    def _build_content(self, snapshot_id: str, text_path: Path, image_path: Path | None) -> list[dict[str, Any]]:
        if self.mode == "llm_text":
            return [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Extract WeChat task data from this text fixture using the shared extraction rules. "
                                f"snapshot_id={snapshot_id}\n\n{text_path.read_text(encoding='utf-8')}"
                            ),
                        }
                    ],
                }
            ]

        if not image_path:
            raise RuntimeError("llm_vision mode requires an image_path")
        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Extract WeChat task data from this screenshot using the exact same extraction rules "
                            "as llm_text. Preserve visible source times and raw message text as accurately as possible. "
                            f"snapshot_id={snapshot_id}"
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{encoded}",
                    },
                ],
            }
        ]
