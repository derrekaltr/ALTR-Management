#!/usr/bin/env python3
"""Findings schema for weekly client analysis + a lightweight validator.

Usage:
    python3 src/schema.py data/weeks/2026-08-08/*.json   # validate findings files
"""
import json
import sys
from pathlib import Path

STATUS_COMPLAINT = {"new", "in_progress", "resolved", "recurring"}
STATUS_COMMITMENT = {"done", "pending", "overdue"}
TRENDS = {"up", "down", "flat", "new"}

# field -> (type, required)
CLIENT_FIELDS = {
    "client": (str, True),
    "slug": (str, True),
    "week_ending": (str, True),
    "summary": (str, True),
    "health": (dict, True),
    "reminders": (list, True),
    "complaints": (list, True),
    "commitments": (list, True),
    "payments": (list, True),
    "client_priorities": (list, True),
    "suggestions": (list, True),
    "wins": (list, True),
    "week_stats": (dict, False),
}

LIST_ITEM_REQUIRED = {
    "reminders": ["employee", "topic", "count"],
    "complaints": ["issue", "status"],
    "commitments": ["what", "who", "status"],
    "payments": ["note"],
}


def validate_client_findings(obj: dict):
    errors = []
    for field, (ftype, required) in CLIENT_FIELDS.items():
        if field not in obj:
            if required:
                errors.append(f"missing field: {field}")
            continue
        if not isinstance(obj[field], ftype):
            errors.append(f"{field}: expected {ftype.__name__}, got {type(obj[field]).__name__}")

    health = obj.get("health", {})
    if isinstance(health, dict):
        score = health.get("score")
        if not isinstance(score, (int, float)) or not 0 <= score <= 100:
            errors.append("health.score must be a number 0-100")
        if health.get("trend") not in TRENDS:
            errors.append(f"health.trend must be one of {sorted(TRENDS)}")
        if not health.get("rationale"):
            errors.append("health.rationale required")

    for field, required_keys in LIST_ITEM_REQUIRED.items():
        for i, item in enumerate(obj.get(field) or []):
            if not isinstance(item, dict):
                errors.append(f"{field}[{i}] must be an object")
                continue
            for key in required_keys:
                if key not in item:
                    errors.append(f"{field}[{i}] missing key: {key}")

    for i, item in enumerate(obj.get("complaints") or []):
        if isinstance(item, dict) and item.get("status") not in STATUS_COMPLAINT:
            errors.append(f"complaints[{i}].status must be one of {sorted(STATUS_COMPLAINT)}")
    for i, item in enumerate(obj.get("commitments") or []):
        if isinstance(item, dict) and item.get("status") not in STATUS_COMMITMENT:
            errors.append(f"commitments[{i}].status must be one of {sorted(STATUS_COMMITMENT)}")
    return errors


def validate_employees(obj: dict):
    errors = []
    if not isinstance(obj.get("employees"), list):
        return ["missing/invalid field: employees (list)"]
    for i, emp in enumerate(obj["employees"]):
        for key in ("name", "summary", "open_issues", "clients"):
            if key not in emp:
                errors.append(f"employees[{i}] missing key: {key}")
    return errors


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    failed = False
    for arg in sys.argv[1:]:
        path = Path(arg)
        obj = json.loads(path.read_text())
        errors = validate_employees(obj) if path.name == "_employees.json" else validate_client_findings(obj)
        if errors:
            failed = True
            print(f"✗ {path.name}")
            for e in errors:
                print(f"    {e}")
        else:
            print(f"✓ {path.name}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
