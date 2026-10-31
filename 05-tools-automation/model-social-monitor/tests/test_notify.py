from model_monitor.notify import MESSAGE_LIMIT, PHOTO_CAPTION_LIMIT, build_caption, truncate


def test_caption_format():
    caption = build_caption(
        "Amber Hayes", "instagram", "Amber is at the beach.", "https://instagram.com/p/x/"
    )
    assert caption.startswith("\U0001f195 Amber Hayes — Instagram")
    assert "Amber is at the beach." in caption
    assert caption.endswith("https://instagram.com/p/x/")


def test_caption_without_url():
    caption = build_caption("Vale Rae", "tiktok", "New GRWM video.", None)
    assert "TikTok" in caption
    assert not caption.endswith("\n")


def test_truncate_short_text_untouched():
    assert truncate("hello", PHOTO_CAPTION_LIMIT) == "hello"


def test_truncate_at_photo_limit():
    long = "x" * 5000
    out = truncate(long, PHOTO_CAPTION_LIMIT)
    assert len(out) <= PHOTO_CAPTION_LIMIT
    assert out.endswith("…")


def test_truncate_at_message_limit():
    out = truncate("y" * 10000, MESSAGE_LIMIT)
    assert len(out) <= MESSAGE_LIMIT
