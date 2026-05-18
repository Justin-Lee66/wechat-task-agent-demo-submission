from agent.models import ExtractedTask
from agent.normalizer import extract_mentions, extract_task_mentions, has_self_mention, normalize_task


def test_self_alias_detection():
    text = "@阿可 @Iris 小秘书 这些都同步进我们的任务表"
    assert extract_mentions(text)[:2] == ["阿可", "Iris"]
    assert has_self_mention(text) is True
    assert has_self_mention("@Henry 这周能不能先给一版") is False


def test_role_prefix_mention_stays_one_person():
    assert extract_mentions("@mkt Chris 需要 support") == ["mkt Chris"]


def test_group_broadcast_mentions_all_demo_people():
    text = "【Year-end Summit】给大家同步一下这次年会物料 deadline"
    assert extract_mentions(text) == []
    assert extract_task_mentions(text) == ["阿可", "Henry", "Iris", "Tara.L", "Chris"]
    assert has_self_mention(text) is True


def test_llm_broadcast_assignees_are_not_action_owners():
    raw_text = (
        "【Year-end Summit】给大家同步一下这次年会物料 deadline:\n"
        "• Final .pptx + .pdf backup — by Monday 5/19"
    )
    extracted = ExtractedTask(
        project="Year-End Summit",
        title="Prepare final .pptx and .pdf backup",
        description="Prepare the final .pptx and .pdf backup materials.",
        assignees=["阿可", "Henry", "Iris", "Tara.L", "Chris"],
        mentioned_users=["阿可", "Henry", "Iris", "Tara.L", "Chris"],
        due_text="Monday 5/19",
        source_message_time="下午 2:02",
        raw_text=raw_text,
    )

    normalized = normalize_task(extracted, "hash", "2pm")

    assert normalized.canonical_key == "year-end-summit|final-pptx-pdf-backup"
    assert normalized.project == "Year-end Summit"
    assert normalized.assignees == []
    assert normalized.mentioned_users == ["阿可", "Henry", "Iris", "Tara.L", "Chris"]
