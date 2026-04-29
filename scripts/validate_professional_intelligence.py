#!/usr/bin/env python3
"""Validate Professional Intelligence DelEx automation fixtures.

This validator intentionally uses only the Python standard library. It implements the
small JSON Schema subset used by this repository's Professional Intelligence schemas:
required, properties, additionalProperties=false, const, enum, primitive type checks,
arrays, object properties, and simple union types.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    (
        ROOT / "contracts/professional-intelligence/work-item.schema.json",
        ROOT / "examples/professional-intelligence/work-item.example.json",
    ),
    (
        ROOT / "contracts/professional-intelligence/demo-acceptance.schema.json",
        ROOT / "examples/professional-intelligence/demo-acceptance.example.json",
    ),
    (
        ROOT / "contracts/professional-intelligence/repo-readiness.schema.json",
        ROOT / "examples/professional-intelligence/repo-readiness.example.json",
    ),
]


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid json in {path}: {exc}") from exc


def json_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def type_matches(value: Any, expected: str) -> bool:
    actual = json_type_name(value)
    if expected == "number":
        return actual in {"integer", "number"}
    return actual == expected


def validate(schema: dict[str, Any], value: Any, path: str = "$") -> None:
    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{path}: expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{path}: {value!r} not in enum {schema['enum']!r}")

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(type_matches(value, item) for item in expected_types):
            raise ValidationError(
                f"{path}: expected type {expected_types!r}, got {json_type_name(value)!r}"
            )

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ValidationError(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                raise ValidationError(f"{path}: unexpected properties {extra!r}")

        additional = schema.get("additionalProperties")
        for key, item in value.items():
            child_schema = properties.get(key)
            if child_schema is None and isinstance(additional, dict):
                child_schema = additional
            if child_schema is not None:
                validate(child_schema, item, f"{path}.{key}")

    if isinstance(value, list):
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                validate(item_schema, item, f"{path}[{index}]")


def main() -> int:
    failures: list[str] = []
    for schema_path, example_path in PAIRS:
        try:
            schema = load_json(schema_path)
            example = load_json(example_path)
            validate(schema, example)
            print(f"ok: {example_path.relative_to(ROOT)} validates against {schema_path.relative_to(ROOT)}")
        except ValidationError as exc:
            failures.append(str(exc))

    if failures:
        print("Professional Intelligence validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Professional Intelligence validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
