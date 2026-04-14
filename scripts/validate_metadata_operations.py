#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
EXAMPLE_DIR = ROOT / "examples"

SECTION_TO_SCHEMA = {
    "kmass_metric": "kmass-metric.schema.json",
    "metadata_contact_assignment": "metadata-contact-assignment.schema.json",
    "metadata_completeness_evaluation": "metadata-completeness-evaluation.schema.json",
    "metadata_inconsistency_finding": "metadata-inconsistency-finding.schema.json",
    "metadata_escalation_event": "metadata-escalation-event.schema.json",
    "metadata_sla_policy": "metadata-sla-policy.schema.json",
}


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    validators = {
        section: Draft202012Validator(load_json(SCHEMA_DIR / schema_name), format_checker=FormatChecker())
        for section, schema_name in SECTION_TO_SCHEMA.items()
    }

    paths = sorted(EXAMPLE_DIR.glob("metadata-remediation-*.yaml"))
    if not paths:
        print("[FAIL] no metadata remediation examples found", file=sys.stderr)
        return 2

    failures: list[str] = []

    for path in paths:
        payload = load_yaml(path)
        for section, validator in validators.items():
            if section not in payload:
                failures.append(f"{path.name}: missing section '{section}'")
                continue
            obj = payload[section]
            for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.path)):
                field_path = "/".join(str(p) for p in err.path)
                failures.append(f"{path.name}:{section}:{field_path or '<root>'}: {err.message}")

        if failures:
            continue

        artifact_id = payload["metadata_contact_assignment"]["artifact_id"]
        if payload["metadata_completeness_evaluation"]["artifact_id"] != artifact_id:
            failures.append(f"{path.name}: completeness artifact_id mismatch")
        if payload["metadata_inconsistency_finding"]["artifact_id"] != artifact_id:
            failures.append(f"{path.name}: inconsistency artifact_id mismatch")
        if payload["metadata_escalation_event"]["artifact_id"] != artifact_id:
            failures.append(f"{path.name}: escalation artifact_id mismatch")
        if payload["metadata_escalation_event"]["severity"] != payload["metadata_sla_policy"]["severity"]:
            failures.append(f"{path.name}: escalation severity must match SLA severity in this example")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1

    print("[OK] metadata operations examples validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
