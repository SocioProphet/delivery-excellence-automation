#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "bounty-program-policy.schema.json"
EXAMPLE_DIR = ROOT / "examples"


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    validator = Draft202012Validator(load_json(SCHEMA))
    paths = sorted(EXAMPLE_DIR.glob("*.bounty-policy.yaml"))
    if not paths:
        print("[FAIL] no *.bounty-policy.yaml examples found", file=sys.stderr)
        return 2

    failures: list[str] = []
    for path in paths:
        policy = load_yaml(path)
        prefix = path.name.removesuffix(".bounty-policy.yaml")
        bundle_path = EXAMPLE_DIR / f"{prefix}.bundle.yaml"
        engagement_path = EXAMPLE_DIR / f"{prefix}.engagement.yaml"

        for err in sorted(validator.iter_errors(policy), key=lambda e: list(e.path)):
            field_path = "/".join(str(p) for p in err.path)
            failures.append(f"{path.name}: {field_path or '<root>'}: {err.message}")

        if failures:
            continue

        if not bundle_path.exists():
            failures.append(f"{path.name}: missing sibling bundle example {bundle_path.name}")
            continue
        if not engagement_path.exists():
            failures.append(f"{path.name}: missing sibling engagement example {engagement_path.name}")
            continue

        bundle = load_yaml(bundle_path)
        engagement = load_yaml(engagement_path)
        gate_ids = {g["gate_id"] for g in bundle.get("delivery_gates", [])}
        service_offer_id = bundle.get("service_offer", {}).get("offer_id")
        engagement_id = engagement.get("engagement_id")

        if policy["service_offer_id"] != service_offer_id:
            failures.append(
                f"{path.name}: service_offer_id '{policy['service_offer_id']}' does not match bundle offer_id '{service_offer_id}'"
            )
        if policy.get("engagement_id") and policy["engagement_id"] != engagement_id:
            failures.append(
                f"{path.name}: engagement_id '{policy['engagement_id']}' does not match engagement example '{engagement_id}'"
            )
        for gate_id in policy.get("gate_requirements", []):
            if gate_id not in gate_ids:
                failures.append(f"{path.name}: unknown gate requirement '{gate_id}'")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1

    print("[OK] incentive policies validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
