from agent.dedupe import canonical_project, canonical_task_key, canonical_title, message_hash


def test_message_hash_dedupes_same_message_across_snapshots():
    raw = "【Solene】3 天内完成主视觉海报首版"
    assert message_hash("下午 12:09", "Coco-某地产", raw) == message_hash("下午 12:09", "Coco-某地产", raw)


def test_known_canonical_task_key():
    assert canonical_task_key("Solene", "Main visual poster first version") == "solene|main-visual-poster-first-version"
    assert canonical_task_key("Belmont", "Yoyo + Jason YouTube video") == "belmont|yoyo-jason-youtube-video"


def test_llm_vision_title_variants_map_to_fixture_canonical_keys():
    variants = [
        (
            "General Marketing",
            "Post yesterday's event content to social channels",
            "Post yesterday's event content to WeChat Moments, LinkedIn, and Instagram; choose attractive images.",
            "social-content|yesterday-event-social-publishing",
        ),
        (
            "Social Media",
            "Review yesterday event social post images",
            "Review the images/content for yesterday's event social posts.",
            "social-content|yesterday-event-social-publishing",
        ),
        (
            "Solene",
            "Finalize main key visual poster layout",
            "One main image with property, selling points, and price, plus one information graphic with map and features.",
            "solene|main-visual-poster-first-version",
        ),
        (
            "1847 HUDSON BLVD",
            "Update official website description",
            "Update official website description together with arrival directions updates.",
            "1847-hudson-blvd|arrival-map-address-description",
        ),
        (
            "1847 Hudson Blvd",
            "Create arrival guide map and update address instructions",
            "Create arrival guide map and clearly mark the correct address input method and route.",
            "1847-hudson-blvd|arrival-map-address-description",
        ),
        (
            "Belmont",
            "Update neighborhood videos in broker folder and coordinate publishing",
            "Ensure neighborhood videos are updated into the broker folder and coordinate Instagram, Xiaohongshu, and ads.",
            "belmont|broker-folder-social-ads-video-update",
        ),
        (
            "Verona",
            "Deliver Verona photos before video and room tour",
            "Prioritize Verona photos first due to tight timing, then work on the company video and room tour later.",
            "verona|photo-first-version",
        ),
        (
            "Company Website / Agent Portal",
            "Add regional introduction copy to agent portal and company blog",
            "Add regional introduction copy to the agent frontend and company website blog section.",
            "company-blog-agent-front-desk|district-intro-copy",
        ),
        (
            "Year-End Summit",
            "Prepare final .pptx and .pdf backup",
            "Prepare the final .pptx and .pdf backup materials.",
            "year-end-summit|final-pptx-pdf-backup",
        ),
        (
            "Year-end Summit",
            "Prepare final timed run-of-show with cues",
            "Prepare the final timed run-of-show with cues.",
            "year-end-summit|final-timed-run-of-show",
        ),
    ]

    for project, title, description, expected in variants:
        assert canonical_task_key(project, title, description) == expected


def test_llm_vision_project_and_title_are_canonicalized_for_display():
    project = canonical_project(
        "Company Website / Agent Portal",
        "Add regional introduction copy to agent portal and company blog",
    )
    assert project == "Company Blog / Agent Front Desk"
    assert (
        canonical_title("Social Media", "Review yesterday event social post images")
        == "Yesterday event social publishing"
    )
