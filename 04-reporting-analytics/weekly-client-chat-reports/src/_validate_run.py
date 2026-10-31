"""Check every analyst file in a cs-gaps run parses and has all 10 dimensions.

Usage: python3 src/_validate_run.py data/analysis/cs-gaps-<DATE>
"""
import glob
import json
import os
import sys

DIMS = ["responsiveness", "follow_through", "proactive_communication", "onboarding_handoff",
        "chatter_conduct", "platform_health", "billing_ops", "ownership_escalation",
        "disengagement_detection", "security_hygiene"]

for f in sorted(glob.glob(os.path.join(sys.argv[1], "*.json"))):
    name = os.path.basename(f)
    if name.startswith("_"):
        continue
    try:
        d = json.load(open(f))
    except json.JSONDecodeError as e:
        print(f"BAD JSON  {name}: {e}")
        continue
    missing = [k for k in DIMS if k not in d.get("dimensions", {})]
    sev = {k: d["dimensions"][k].get("severity") for k in DIMS if k in d.get("dimensions", {})}
    print(f"ok  {name:28} {d.get('status'):8} last={d.get('last_client_message')} "
          f"sum={sum(v for v in sev.values() if isinstance(v, int))} missing={missing or '-'}")
