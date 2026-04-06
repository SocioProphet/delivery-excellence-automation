#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "engagement.schema.json"
EXAMPLE_DIR = ROOT / "examples"


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    validator = Draft202012Validator(load_json(SCHEMA))
    paths = sorted(EXAMPLE_DIR.glob("*.engagement.yaml"))
    if not paths:
        print("[FAIL] no *.engagement.yaml examples found", file=sys.stderr)
        return 2

    failures: list[str] = []
    for path in paths:
      obj = load_yaml(path)
      for err in sorted(validator.iter_errors(obj), key=lambda e: list(e.path)):
          field_path = "/".join(str(p) for p in err.path)
          failures.append(f"{path.name}: {field_path or '<root>'}: {err.message}")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}", file=sys.stderr)
        return 1

    print("[OK] engagement objects validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
