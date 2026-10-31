#!/usr/bin/env python3
"""Cross-reference target IG handles against Derrek's official IG data export
(data/ig-export/): produces data/export_flags.json with you_follow / follows_you /
close-friend info per target. The export is from May 2026 — treat as a floor,
live browsing refreshes it."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPORT = ROOT / "data" / "ig-export"


def usernames_from(path, key=None):
    data = json.loads(path.read_text())
    entries = data[key] if key else data
    out = set()
    for e in entries:
        if e.get("title"):
            out.add(e["title"].lower())
        for s in e.get("string_list_data", []):
            if s.get("value"):
                out.add(s["value"].lower())
    return out


following = usernames_from(EXPORT / "following.json", "relationships_following")
followers = set()
for shard in sorted(EXPORT.glob("followers_*.json")):
    followers |= usernames_from(shard)
close_friends = set()
for e in json.loads((EXPORT / "close_friends.json").read_text()):
    for lv in e.get("label_values", []):
        if lv.get("label") == "Username" and lv.get("value"):
            close_friends.add(lv["value"].lower())

targets = json.loads((ROOT / "data" / "targets.json").read_text())["targets"]
flags = {}
for t in targets:
    ig = (t.get("ig_handle") or "").lower()
    if not ig:
        continue
    flags[ig] = {
        "handle": t["handle"],
        "you_follow": ig in following,
        "follows_you": ig in followers,
    }

out = {
    "_meta": {
        "export_date": "2026-05-21",
        "following_count": len(following),
        "followers_count": len(followers),
        "close_friends_count": len(close_friends),
    },
    "targets": flags,
}
(ROOT / "data" / "export_flags.json").write_text(json.dumps(out, indent=2))

hits = {k: v for k, v in flags.items() if v["you_follow"] or v["follows_you"]}
print(f"following={len(following)} followers={len(followers)} close_friends={len(close_friends)}")
print(f"targets with IG handle: {len(flags)}; direct hits: {len(hits)}")
for k, v in hits.items():
    print(f"  @{k}: you_follow={v['you_follow']} follows_you={v['follows_you']}")
