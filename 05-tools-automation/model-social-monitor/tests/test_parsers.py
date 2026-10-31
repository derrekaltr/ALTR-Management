import json
from pathlib import Path

from model_monitor.sources import instagram, stories, tiktok

FIXTURES = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text())


def test_instagram_parser():
    posts = instagram.parse_items(load("ig_items.json"))
    # error item and malformed item are dropped
    assert len(posts) == 2

    beach = posts[0]
    assert beach.platform == "instagram"
    assert beach.post_id == "3456789012345678901"
    assert beach.handle == "amberhayes"  # lowercased for routing
    assert "Beach day" in beach.caption
    assert beach.image_url.endswith("beach.jpg?sig=abc")
    assert beach.post_url == "https://www.instagram.com/p/DAbCdEfGhIj/"
    assert beach.timestamp.year == 2026

    carousel = posts[1]
    assert carousel.handle == "sarah.h"
    assert "carousel1" in carousel.image_url  # Sidecar falls back to first image


def test_tiktok_parser():
    posts = tiktok.parse_items(load("tiktok_items.json"))
    # errorCode item dropped
    assert len(posts) == 2

    grwm = posts[0]
    assert grwm.platform == "tiktok"
    assert grwm.post_id == "7412345678901234567"
    assert grwm.handle == "vale.rae"
    assert grwm.image_url.startswith("https://p16-sign-va.tiktokcdn.com/")
    assert grwm.post_url.endswith("/video/7412345678901234567")
    assert grwm.timestamp.isoformat().startswith("2026-09-25")

    no_cover = posts[1]
    assert no_cover.image_url is None  # empty videoMeta tolerated
    assert no_cover.caption == ""
    assert no_cover.timestamp is not None  # falls back to unix createTime


def test_stories_parser():
    posts = stories.parse_items(load("story_items.json"))
    # sponsored story, highlight, and diagnostic row are all dropped
    assert len(posts) == 2

    beach = posts[0]
    assert beach.platform == "instagram_story"
    assert beach.post_id == "3489001122334455667"
    assert beach.handle == "amberhayes"
    assert beach.caption == "beach dayyy"
    assert beach.timestamp is not None  # unix takenAt parsed
    assert beach.image_url.endswith("story1.jpg?sig=abc")
    assert beach.post_url == (
        "https://www.instagram.com/stories/amberhayes/3489001122334455667/"
    )

    video = posts[1]
    assert video.handle == "vale.rae"
    assert video.timestamp.isoformat().startswith("2026-09-26")  # ISO takenAt parsed
    assert "story2_cover" in video.image_url  # video story uses its cover image


def test_parsers_tolerate_garbage():
    assert instagram.parse_items([None, 42, {}, {"id": "x"}]) == []
    assert tiktok.parse_items([None, "str", {}, {"id": "x"}]) == []
    assert stories.parse_items([None, "str", {}, {"storyId": "x"}]) == []
