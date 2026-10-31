from snapstar_review.config import DEFAULTS
from snapstar_review.models import (
    CaptureStatus,
    Category,
    CreatorReview,
    ItemReview,
    ReviewedItem,
    Severity,
    Surface,
)
from snapstar_review.rubric import readiness_level, weighted_score

SCORING = DEFAULTS["scoring"]


def make_review(severities: list[Severity]) -> CreatorReview:
    return CreatorReview(
        username="test",
        items=[
            ReviewedItem(
                item_id=f"i{i}",
                surface=Surface.STORY,
                review=ItemReview(severity=s, rationale="x"),
            )
            for i, s in enumerate(severities)
        ],
    )


def test_all_clean_is_ready():
    review = make_review([Severity.CLEAN, Severity.CLEAN])
    assert weighted_score(review, SCORING) == 0
    assert readiness_level(review, SCORING) == "ready"


def test_single_low_is_nearly_ready():
    review = make_review([Severity.LOW, Severity.CLEAN])
    assert weighted_score(review, SCORING) == 1
    assert readiness_level(review, SCORING) == "nearly_ready"


def test_high_and_medium_needs_cleanup():
    review = make_review([Severity.HIGH, Severity.MEDIUM])
    assert weighted_score(review, SCORING) == 14
    assert readiness_level(review, SCORING) == "needs_cleanup"


def test_any_critical_forces_major_cleanup():
    review = make_review([Severity.CRITICAL])
    assert readiness_level(review, SCORING) == "major_cleanup"


def test_many_highs_exceed_needs_cleanup_threshold():
    review = make_review([Severity.HIGH, Severity.HIGH, Severity.HIGH])
    assert weighted_score(review, SCORING) == 30
    assert readiness_level(review, SCORING) == "major_cleanup"


def test_flagged_items_sorted_by_severity():
    review = make_review([Severity.LOW, Severity.CRITICAL, Severity.CLEAN, Severity.MEDIUM])
    flagged = review.flagged_items()
    assert [i.review.severity for i in flagged] == [
        Severity.CRITICAL,
        Severity.MEDIUM,
        Severity.LOW,
    ]


def test_severity_counts():
    review = make_review([Severity.HIGH, Severity.HIGH, Severity.CLEAN])
    counts = review.severity_counts()
    assert counts["high"] == 2
    assert counts["clean"] == 1
    assert counts["critical"] == 0


def test_item_review_parses_from_json():
    raw = {
        "severity": "high",
        "categories": ["revealing_attire", "suggestive_pose"],
        "rationale": "why",
        "removal_action": "how",
        "borderline": True,
    }
    review = ItemReview(**raw)
    assert review.severity == Severity.HIGH
    assert Category.SUGGESTIVE_POSE in review.categories


def test_non_ok_status_roundtrip():
    review = CreatorReview(username="x", status=CaptureStatus.BOT_WALL)
    loaded = CreatorReview.model_validate_json(review.model_dump_json())
    assert loaded.status == CaptureStatus.BOT_WALL
    assert loaded.items == []
