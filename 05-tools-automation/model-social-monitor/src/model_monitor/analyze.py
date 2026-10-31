"""Turn a post (caption + image) into a short chatter-facing update via Claude.

Claude also acts as the relevance gate: posts that tell chatters nothing
useful about the model's real life (ads, giveaways, meme reposts, cross-promo)
come back as not relevant and are never sent to the channel.
"""

from __future__ import annotations

import base64
import json
import logging

import anthropic

from .sources import PLATFORM_LABELS, Post

log = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = (
    "You write short internal updates for chat staff at a talent-management agency. "
    "Staff chat with fans on the talent's behalf and need to know what the model just "
    "posted publicly so they can reference it naturally in conversation.\n\n"
    "First decide whether this post shows the staff something about the model's real "
    "life right now: where she is, what she is doing, how she looks, her mood, travel, "
    "life events (surgery, birthday, vacation, moving), pets, family moments — anything "
    "a fan might see and bring up.\n\n"
    "NOT relevant — always skip: sponsored posts and brand ads; giveaways, discount "
    "codes, promo announcements; press coverage, articles, interviews, podcast or event "
    "appearances and any 'featured in' announcements; promotion of fights, shows, or "
    "events; reposts or shares of other people's content; shoutouts and cross-promotion "
    "of other creators or friends; memes, quote graphics, engagement-bait.\n\n"
    "The test: does the staff learn where she is or what is happening in her personal "
    "life from this? If the post's main purpose is to promote or announce anything — "
    "content, coverage, an event, another person — mark it not relevant, even if she "
    "appears in it or is mentioned by it. Only a post that genuinely shows her own life "
    "should get the benefit of the doubt when details are unclear.\n\n"
    "Also mark it not relevant if it shows essentially the same thing as an update the "
    "staff already received in the last two days (listed under 'Already sent'): same "
    "scene, same location, same activity, same items — a second story of the same "
    "beach day or the same bouquet is noise. Judge only against that list: it "
    "deliberately covers just the last two days, because the same activity happening "
    "again after a longer gap (another beach day next month, another trip) is genuinely "
    "new and must be sent. Within the list, send again only when something meaningfully "
    "changed — a new location, activity, outfit, or piece of news.\n\n"
    "Do all of your thinking silently before answering. Your entire reply must be "
    "exactly one JSON object — no explanation, no reconsideration, no text before or "
    "after it, no markdown fences:\n"
    '{\"relevant\": true, \"summary\": \"...\"} or {\"relevant\": false, \"summary\": \"\"}\n\n'
    "When relevant, the summary must contain: (1) one or two sentences describing what "
    "she posted — outfit, location, activity, mood, anything visually notable; (2) one "
    "line starting with 'Conversation hook:' suggesting how a chatter could bring it up "
    "with fans. Plain text inside the JSON string, no markdown, under 700 characters. "
    "Refer to the model by her first name. For an Instagram Story, remember it "
    "disappears after 24 hours, so treat it as what she is doing right now."
)


def _parse_response(raw: str) -> str | None:
    """Return the summary, or None if the post was judged not relevant.

    The model occasionally deliberates in text and emits more than one JSON
    object; we obey the LAST valid verdict (its final answer). If no valid
    verdict exists we raise — never post raw model output to a channel — and
    the pipeline's retry logic takes it from there.
    """
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    decoder = json.JSONDecoder()
    verdicts: list[dict] = []
    idx = 0
    while True:
        start = text.find("{", idx)
        if start == -1:
            break
        try:
            obj, end = decoder.raw_decode(text, start)
        except ValueError:
            idx = start + 1
            continue
        if isinstance(obj, dict) and "relevant" in obj:
            verdicts.append(obj)
        idx = end

    if not verdicts:
        log.warning("relevance response had no valid verdict JSON: %r", raw[:200])
        raise RuntimeError("Claude's relevance response could not be parsed")
    if len(verdicts) > 1:
        log.warning("relevance response contained %d verdicts; using the last", len(verdicts))

    data = verdicts[-1]
    if not data.get("relevant"):
        return None
    summary = str(data.get("summary") or "").strip()
    return summary or None


def summarize_post(
    client: anthropic.Anthropic,
    model_name: str,
    post: Post,
    image: tuple[bytes, str] | None,
    recent_updates: list[str] | None = None,
) -> str | None:
    """Returns the chatter-facing summary, or None if the post isn't worth sending.

    recent_updates: summaries already sent for this model in the last day, so
    near-duplicate posts (e.g. two stories of the same moment) get skipped.
    Raises anthropic.APIError on failure; the pipeline handles retries.
    """
    posted = post.timestamp.isoformat() if post.timestamp else "unknown"
    text = (
        f"Model: {model_name}\n"
        f"Platform: {PLATFORM_LABELS.get(post.platform, post.platform)}\n"
        f"Posted: {posted}\n"
        f"Caption: {post.caption.strip() or '(no caption)'}"
    )
    if recent_updates:
        text += "\n\nAlready sent to staff in the last two days:\n" + "\n".join(
            f"- {u}" for u in recent_updates
        )

    content: list[dict] = []
    if image is not None:
        data, media_type = image
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64.standard_b64encode(data).decode("ascii"),
                },
            }
        )
    content.append({"type": "text", "text": text})

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )
    raw = "".join(block.text for block in response.content if block.type == "text")
    if not raw.strip():
        raise RuntimeError("Claude returned an empty response")
    return _parse_response(raw)
