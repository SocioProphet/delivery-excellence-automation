#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
EXAMPLE_DIR = ROOT / "examples"


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    payout_validator = Draft202012Validator(load_json(SCHEMA_DIR / "payout-decision.schema.json"))
    escrow_validator = Draft202012Validator(load_json(SCHEMA_DIR / "escrow-reference.schema.json"))

    paths = sorted(EXAMPLE_DIR.glob("*.payout.yaml"))
    if not paths:
        print("[FAIL] no *.payout.yaml examples found", file=sys.stderr)
        return 2

    failures: list[str] = []

    for path in paths:
        payload = load_yaml(path)
        prefix = path.name.removesuffix(".payout.yaml")
        bundle_path = EXAMPLE_DIR / f"{prefix}.bundle.yaml"
        engagement_path = EXAMPLE_DIR / f"{prefix}.engagement.yaml"

        if "payout_decision" not in payload:
            failures.append(f"{path.name}: missing payout_decision")
            continue
        if "escrow_reference" not in payload:
            failures.append(f"{path.name}: missing escrow_reference")
            continue

        payout = payload["payout_decision"]
        escrow = payload["escrow_reference"]

        for err in sorted(payout_validator.iter_errors(payout), key=lambda e: list(e.path)):
            field_path = "/".join(str(p) for p in err.path)
            failures.append(f"{path.name}:payout_decision:{field_path or '<root>'}: {err.message}")
        for err in sorted(escrow_validator.iter_errors(escrow), key=lambda e: list(e.path)):
            field_path = "/".join(str(p) for p in err.path)
            failures.append(f"{path.name}:escrow_reference:{field_path or '<root>'}: {err.message}")

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
        reusable_asset_ids = {a["asset_id"] for a in bundle.get("reusable_assets", [])}
        exception_ids = {e["exception_id"] for e in bundle.get("exception_classes", [])}
        evidence_universe = set(bundle.get("control_loop", {}).get("emitted_evidence", []))
        for gate in bundle.get("delivery_gates", []):
            evidence_universe |= set(gate.get("required_evidence", []))
        for item in bundle.get("board_items", []):
            evidence_universe |= set(item.get("evidence_links", []))

        if payout["engagement_id"] != engagement["engagement_id"]:
            failures.append(
                f"{path.name}: payout engagement_id '{payout['engagement_id']}' does not match engagement example '{engagement['engagement_id']}'"
            )
        if payout["gate_id"] not in gate_ids:
            failures.append(f"{path.name}: unknown gate_id '{payout['gate_id']}'")
        if payout.get("escrow_reference_id") != escrow["escrow_reference_id"]:
            failures.append(f"{path.name}: escrow reference mismatch between payout decision and escrow object")

        for asset_id in payout.get("reusable_asset_ids", []):
            if asset_id not in reusable_asset_ids:
                failures.append(f"{path.name}: unknown reusable_asset_id '{asset_id}'")
        for exception_id in payout.get("exception_ids", []):
            if exception_id not in exception_ids:
                failures.append(f"{path.name}: unknown exception_id '{exception_id}'")
        for evidence in payout.get("evidence_links", []):
            if evidence not in evidence_universe:
                failures.append(f"{path.name}: evidence link '{evidence}' not found in sibling bundle evidence universe")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1

    print("[OK] payout and escrow objects validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
