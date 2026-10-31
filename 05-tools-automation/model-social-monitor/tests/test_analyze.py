import pytest

from model_monitor.analyze import _parse_response


def test_relevant_post_returns_summary():
    raw = '{"relevant": true, "summary": "Amber is at the beach. Conversation hook: ask about beach days."}'
    assert _parse_response(raw).startswith("Amber is at the beach.")


def test_irrelevant_post_returns_none():
    assert _parse_response('{"relevant": false, "summary": ""}') is None


def test_irrelevant_with_stray_summary_still_skipped():
    assert _parse_response('{"relevant": false, "summary": "brand giveaway repost"}') is None


def test_json_in_code_fence_is_parsed():
    raw = '```json\n{"relevant": true, "summary": "New GRWM video."}\n```'
    assert _parse_response(raw) == "New GRWM video."


def test_no_verdict_raises_instead_of_posting_raw_text():
    # Raw model output must never reach a channel; the pipeline retries instead.
    with pytest.raises(RuntimeError):
        _parse_response("Amber posted a gym selfie.")


def test_deliberation_with_two_verdicts_obeys_the_last():
    # Real incident: model emitted a verdict, reconsidered in prose, then
    # emitted its final verdict. The whole mess was posted to a channel.
    raw = (
        '{"relevant": true, "summary": "Ebony is hosting an invite-only private '
        'content day tomorrow in Las Vegas.", "summary": ""}\n\n'
        "Wait, let me reconsider. This is an event announcement post promoting her "
        "private experience. The main purpose is to promote the event, not to show "
        "her personal life.\n\n"
        '{"relevant": false, "summary": ""}'
    )
    assert _parse_response(raw) is None


def test_prose_around_single_verdict_is_tolerated():
    raw = 'Here is my assessment:\n{"relevant": true, "summary": "Dani is at the pool."}'
    assert _parse_response(raw) == "Dani is at the pool."


def test_relevant_but_empty_summary_returns_none():
    assert _parse_response('{"relevant": true, "summary": ""}') is None
