"""Validate the Lauryn 2026-09-25 CS gap JSON and clean up working files."""
import json
import os

OUT = "data/analysis/cs-gaps-2026-09-25/lauryn-x-altr.json"
d = json.load(open(OUT))
req = ["client", "slug", "status", "status_reason", "last_client_message",
       "dimensions", "metrics", "what_client_wanted", "what_worked", "top_fix"]
missing = [k for k in req if k not in d]
assert not missing, missing
dims = ["responsiveness", "follow_through", "proactive_communication", "onboarding_handoff",
        "chatter_conduct", "platform_health", "billing_ops", "ownership_escalation",
        "disengagement_detection", "security_hygiene"]
assert sorted(d["dimensions"]) == sorted(dims), set(dims) ^ set(d["dimensions"])
for k in dims:
    v = d["dimensions"][k]
    assert v["severity"] in (0, 1, 2, 3), k
    assert v["internal_failure"]
    assert 2 <= len(v["evidence"]) <= 3, (k, len(v["evidence"]))
    for e in v["evidence"]:
        assert set(e) == {"quote", "who", "date"}, (k, e)
        assert len(e["date"]) == 10, (k, e["date"])
print("VALID:", OUT)
print("status:", d["status"], "| last client msg:", d["last_client_message"])
print("severities:", {k: d["dimensions"][k]["severity"] for k in dims})

for f in ("data/analysis/cs-gaps-2026-09-25/_transcript_lauryn.txt",):
    if os.path.exists(f):
        os.remove(f)
        print("removed", f)
print("dir:", sorted(os.listdir("data/analysis/cs-gaps-2026-09-25")))
