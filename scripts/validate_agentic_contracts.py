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

BUNDLE_SPEC = {
    "service_offer": "service-offer.schema.json",
    "control_loop": "control-loop.schema.json",
    "autonomy_envelope": "autonomy-envelope.schema.json",
    "delivery_gates": "delivery-gate.schema.json",
    "client_dependencies": "client-dependency.schema.json",
    "exception_classes": "exception-class.schema.json",
    "board_items": "board-item.schema.json",
    "reusable_assets": "reusable-asset.schema.json",
    "customer_success_review": "customer-success-review.schema.json",
    "gate_review": "gate-review.schema.json",
}


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_one(validator: Draft202012Validator, obj: object, label: str) -> list[str]:
    errors = []
    for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.path)):
        path = "/".join(str(p) for p in err.path)
        errors.append(f"{label}: {path or '<root>'}: {err.message}")
    return errors


def main() -> int:
    validators = {
        name: Draft202012Validator(load_json(SCHEMA_DIR / schema_file))
        for name, schema_file in BUNDLE_SPEC.items()
    }

    bundle_paths = sorted(EXAMPLE_DIR.glob("*.bundle.yaml"))
    if not bundle_paths:
        print("[FAIL] no *.bundle.yaml examples found", file=sys.stderr)
        return 2

    failures: list[str] = []

    for bundle_path in bundle_paths:
        bundle = load_yaml(bundle_path)
        for section_name, schema_file in BUNDLE_SPEC.items():
            if section_name not in bundle:
                failures.append(f"{bundle_path.name}: missing section '{section_name}'")
                continue
            payload = bundle[section_name]
            validator = validators[section_name]
            if isinstance(payload, list):
                for idx, item in enumerate(payload):
                    failures.extend(validate_one(validator, item, f"{bundle_path.name}:{section_name}[{idx}]"))
            else:
                failures.extend(validate_one(validator, payload, f"{bundle_path.name}:{section_name}"))

        if failures:
            continue

        gate_ids = {g["gate_id"] for g in bundle["delivery_gates"]}
        known_action_classes = {a["class"] for a in bundle["autonomy_envelope"]["actions"]}
        control_loop_id = bundle["control_loop"]["control_loop_id"]

        if bundle["gate_review"]["gate_id"] not in gate_ids:
            failures.append(
                f"{bundle_path.name}: gate_review.gate_id '{bundle['gate_review']['gate_id']}' not found in delivery_gates"
            )

        for item in bundle["board_items"]:
            if item["current_gate"] not in gate_ids:
                failures.append(
                    f"{bundle_path.name}: board item '{item['item_id']}' references unknown gate '{item['current_gate']}'"
                )
            if item["linked_control_loop"] != control_loop_id:
                failures.append(
                    f"{bundle_path.name}: board item '{item['item_id']}' linked_control_loop must match bundle control loop"
                )

        for action_class in bundle["gate_review"]["current_action_classes"]:
            if action_class not in known_action_classes:
                failures.append(
                    f"{bundle_path.name}: gate review references unknown action class '{action_class}'"
                )

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1

    print("[OK] agentic contract bundles validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
