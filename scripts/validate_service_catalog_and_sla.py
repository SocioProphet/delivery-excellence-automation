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
    service_validator = Draft202012Validator(load_json(SCHEMA_DIR / "service-catalog-entry.schema.json"))
    sla_validator = Draft202012Validator(load_json(SCHEMA_DIR / "service-level-agreement.schema.json"))

    paths = sorted(EXAMPLE_DIR.glob("coc-service-catalog-and-sla.yaml"))
    if not paths:
        print("[FAIL] no service catalog + SLA examples found", file=sys.stderr)
        return 2

    failures: list[str] = []
    for path in paths:
        payload = load_yaml(path)
        if "service_catalog_entry" not in payload:
            failures.append(f"{path.name}: missing service_catalog_entry")
            continue
        if "service_level_agreement" not in payload:
            failures.append(f"{path.name}: missing service_level_agreement")
            continue

        service = payload["service_catalog_entry"]
        sla = payload["service_level_agreement"]

        for err in sorted(service_validator.iter_errors(service), key=lambda e: list(e.path)):
            field_path = "/".join(str(p) for p in err.path)
            failures.append(f"{path.name}:service_catalog_entry:{field_path or '<root>'}: {err.message}")
        for err in sorted(sla_validator.iter_errors(sla), key=lambda e: list(e.path)):
            field_path = "/".join(str(p) for p in err.path)
            failures.append(f"{path.name}:service_level_agreement:{field_path or '<root>'}: {err.message}")

        if failures:
            continue

        if service["service_id"] != sla["service_id"]:
            failures.append(f"{path.name}: service_id mismatch between service catalog entry and SLA")
        if service["service_name"] != sla["service_name"]:
            failures.append(f"{path.name}: service_name mismatch between service catalog entry and SLA")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1

    print("[OK] service catalog and SLA examples validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
