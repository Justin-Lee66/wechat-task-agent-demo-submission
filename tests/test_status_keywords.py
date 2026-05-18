from agent.normalizer import detect_status


def test_done_status_keywords():
    assert detect_status("视频已发 YouTube") == "done"
    assert detect_status("done.") == "done"
    assert detect_status("published to Instagram") == "done"
    assert detect_status("still working") == "todo"

