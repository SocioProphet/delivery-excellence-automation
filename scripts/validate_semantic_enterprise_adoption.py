#!/usr/bin/env python3
"""Validate Semantic Enterprise v0.1 adoption coverage fixtures.

This validator is intentionally standard-library-only. It performs both a small
JSON Schema subset validation and semantic checks specific to the estate-level
Semantic Enterprise adoption loop.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "contracts/semantic-enterprise/adoption-coverage.schema.json"
EXAMPLE_PATH = ROOT / "examples/semantic-enterprise/adoption-coverage.example.json"

EXPECTED_REPOS = {
    "SocioProphet/prophet-platform",
    "SocioProphet/sherlock-search",
    "SocioProphet/policy-fabric",
    "SocioProphet/agentplane",
    "SourceOS-Linux/sourceos-syncd",
    "SocioProphet/delivery-excellence-automation",
}

COVERAGE_FLAGS = {
    "manifestImporter",
    "scenarioCoverage",
    "queryCoverage",
    "namedGraphCoverage",
    "provenancePreserved",
    "validationWired",
    "docsPresent",
}

CLOSURE_FLAGS = {"insideSource", "outsideRuntime", "boundaryMembrane", "feedbackSurface"}
COMPLETED_STATUSES = {"merged", "validated"}


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
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


def validate_schema(schema: dict[str, Any], value: Any, path: str = "$.") -> None:
    if "const" in schema and value != schema["const"]:
        raise ValidationError(f"{path}: expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{path}: {value!r} not in enum {schema['enum']!r}")

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(type_matches(value, item) for item in expected_types):
            raise ValidationError(f"{path}: expected type {expected_types!r}, got {json_type_name(value)!r}")

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
                validate_schema(child_schema, item, f"{path}{key}.")

    if isinstance(value, list):
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                validate_schema(item_schema, item, f"{path}[{index}].")


def validate_semantics(example: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    source = example.get("sourceRelease", {})
    if source.get("repository") != "SocioProphet/ontogenesis":
        errors.append("sourceRelease.repository must be SocioProphet/ontogenesis")
    if source.get("release") != "semantic-enterprise-v0.1.0":
        errors.append("sourceRelease.release must be semantic-enterprise-v0.1.0")

    repos = example.get("repos", [])
    repo_names = {repo.get("repository") for repo in repos if isinstance(repo, dict)}
    if repo_names != EXPECTED_REPOS:
        errors.append(f"expected repos {sorted(EXPECTED_REPOS)}, got {sorted(repo_names)}")

    completed = 0
    for repo in repos:
        name = repo.get("repository")
        status = repo.get("status")
        if status in COMPLETED_STATUSES:
            completed += 1
            if not repo.get("prRef"):
                errors.append(f"{name}: completed repo must have prRef")
            if not repo.get("mergeCommit"):
                errors.append(f"{name}: completed repo must have mergeCommit")

        coverage = repo.get("coverage", {})
        missing_coverage = COVERAGE_FLAGS.difference(coverage)
        if missing_coverage:
            errors.append(f"{name}: coverage missing {sorted(missing_coverage)}")
        if coverage.get("provenancePreserved") is not True:
            errors.append(f"{name}: provenancePreserved must be true")
        if coverage.get("validationWired") is not True:
            errors.append(f"{name}: validationWired must be true")
        if coverage.get("docsPresent") is not True:
            errors.append(f"{name}: docsPresent must be true")

        closure = repo.get("closure", {})
        missing_closure = CLOSURE_FLAGS.difference(closure)
        if missing_closure:
            errors.append(f"{name}: closure missing {sorted(missing_closure)}")
        for flag in CLOSURE_FLAGS:
            if closure.get(flag) is not True:
                errors.append(f"{name}: closure.{flag} must be true")

        evidence_refs = repo.get("evidenceRefs", [])
        if not evidence_refs:
            errors.append(f"{name}: evidenceRefs must not be empty")

    overall = example.get("overall", {})
    if overall.get("completedRepos") != completed:
        errors.append(f"overall.completedRepos expected {completed}, got {overall.get('completedRepos')}")
    if overall.get("totalRepos") != len(EXPECTED_REPOS):
        errors.append(f"overall.totalRepos expected {len(EXPECTED_REPOS)}, got {overall.get('totalRepos')}")

    coverage_score = overall.get("coverageScore")
    closure_score = overall.get("closureScore")
    if not isinstance(coverage_score, (int, float)) or not 0 <= coverage_score <= 1:
        errors.append("overall.coverageScore must be between 0 and 1")
    if not isinstance(closure_score, (int, float)) or not 0 <= closure_score <= 1:
        errors.append("overall.closureScore must be between 0 and 1")

    if completed < len(EXPECTED_REPOS) and overall.get("status") != "yellow":
        errors.append("overall.status should be yellow until all repos are completed")
    if completed == len(EXPECTED_REPOS) and overall.get("status") != "green":
        errors.append("overall.status should be green when all repos are completed")

    return errors


def main() -> int:
    failures: list[str] = []
    try:
        schema = load_json(SCHEMA_PATH)
        example = load_json(EXAMPLE_PATH)
        validate_schema(schema, example)
        failures.extend(validate_semantics(example))
    except ValidationError as exc:
        failures.append(str(exc))

    if failures:
        print("Semantic Enterprise adoption validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Semantic Enterprise adoption validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
