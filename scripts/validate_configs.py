#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def main() -> int:
    groups = load_yaml(ROOT / "automation/groups/GROUPS.yaml")["groups"]
    gids = {g["id"] for g in groups}

    # Ensure every list/calendar references an existing group_id
    for rel in ["automation/email/EMAIL_LISTS.yaml", "automation/calendar/CALENDARS.yaml", "automation/calendar/MEETINGS.yaml", "automation/identity/RBAC.yaml"]:
        data = load_yaml(ROOT / rel)
        refs = []
        if "lists" in data:
            refs += [x["group_id"] for x in data["lists"]]
        if "calendars" in data:
            refs += [x["group_id"] for x in data["calendars"]]
        if "bindings" in data:
            refs += [x["group_id"] for x in data["bindings"]]
        if "meetings" in data:
            for m in data["meetings"]:
                refs += m.get("participants_group_ids", [])
        missing = sorted(set(refs) - gids)
        if missing:
            print(f"[FAIL] {rel} references unknown group_ids: {missing}", file=sys.stderr)
            return 2

    # Ensure every group that is used for automation has an email address mapping (policy v1)
    used = set()
    rbac = load_yaml(ROOT / "automation/identity/RBAC.yaml")
    used |= {b["group_id"] for b in rbac.get("bindings", [])}
    meetings = load_yaml(ROOT / "automation/calendar/MEETINGS.yaml")
    for m in meetings.get("meetings", []):
        used |= set(m.get("participants_group_ids", []))

    emails = load_yaml(ROOT / "automation/email/EMAIL_LISTS.yaml")
    email_map = {x["group_id"]: x["address"] for x in emails.get("lists", [])}
    missing_email = sorted(g for g in used if g not in email_map)
    if missing_email:
        print(f"[FAIL] Missing EMAIL_LISTS mappings for group_ids: {missing_email}", file=sys.stderr)
        return 3

    print("[OK] group references + email routing validated")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
