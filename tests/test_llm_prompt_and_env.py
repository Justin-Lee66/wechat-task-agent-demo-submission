from agent.env import load_local_env
from agent.extractor_llm import LLMExtractor
from agent.prompts import SYSTEM_PROMPT
from scripts.extractor_compare import run_extractor_compare
from scripts import llm_smoke


def test_load_local_env_reads_file_without_overriding_existing_values(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENAI_API_KEY=local-test-key\n"
        "OPENAI_MODEL=gpt-5.5\n"
        "EXTRACTOR_MODE=llm_text\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("OPENAI_MODEL", "already-set")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("EXTRACTOR_MODE", raising=False)

    load_local_env(env_file)

    assert "OPENAI_API_KEY" in __import__("os").environ
    assert __import__("os").environ["OPENAI_MODEL"] == "already-set"
    assert __import__("os").environ["EXTRACTOR_MODE"] == "llm_text"


def test_llm_prompt_contains_current_extraction_semantics():
    required_phrases = [
        "Mentions must be scoped to the specific bullet",
        "Do not copy a mention from one bullet to other tasks",
        "Solene task: mentioned_users=[]",
        "Belmont task: mentioned_users=[]",
        "Verona task: assignees may include Henry",
        "大家 or 给大家同步一下 mean broadcast/notification, not assignment",
        "Follow-up pronouns such as 这些",
        "Sync Year-end Summit material deadlines into task table",
        "context_raw_texts",
        "Do not assign 阿可 or Iris to the four Year-end Summit production tasks",
        "Return exactly one JSON object",
    ]

    for phrase in required_phrases:
        assert phrase in SYSTEM_PROMPT


def test_llm_smoke_skips_without_key(monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", "")

    llm_smoke.main([])

    assert "llm-smoke skipped: OPENAI_API_KEY is not set." in capsys.readouterr().out


def test_llm_smoke_sanitizes_errors(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "local-secret-test-value")

    message = llm_smoke._sanitize_error("bad key local-secret-test-value failed")

    assert "local-secret-test-value" not in message
    assert "[redacted]" in message


def test_extractor_compare_skips_without_key(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "")

    report = run_extractor_compare("llm_vision", tmp_path / "compare.json")

    assert report == {
        "mode": "llm_vision",
        "status": "skipped",
        "reason": "OPENAI_API_KEY is not set",
    }
    assert not (tmp_path / "compare.json").exists()


def test_llm_text_and_vision_build_responses_inputs(tmp_path):
    text_path = tmp_path / "10am.txt"
    image_path = tmp_path / "wechat_10am.png"
    text_path.write_text("### 上午 09:42\nSolene 这周必须完成主视觉海报首版\n", encoding="utf-8")
    image_path.write_bytes(b"fake-png")

    text_input = LLMExtractor("llm_text")._build_content("10am", text_path, image_path)
    vision_input = LLMExtractor("llm_vision")._build_content("10am", text_path, image_path)

    assert text_input[0]["content"][0]["type"] == "input_text"
    assert "same extraction rules" not in text_input[0]["content"][0]["text"]
    assert "snapshot_id=10am" in text_input[0]["content"][0]["text"]
    assert vision_input[0]["content"][0]["type"] == "input_text"
    assert "same extraction rules" in vision_input[0]["content"][0]["text"]
    assert vision_input[0]["content"][1]["type"] == "input_image"
    assert vision_input[0]["content"][1]["image_url"].startswith("data:image/png;base64,")
