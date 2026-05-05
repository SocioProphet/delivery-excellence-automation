#!/usr/bin/env python3
"""Generate deterministic Agent Harness Delivery Excellence readouts.

The generator consumes a RecentRepoActivityReport and emits a minimal set of
Delivery Excellence artifacts:

- scoreboard-snapshot.generated.json
- delivery-metric-event.generated.json
- customer-proof-readout.generated.json

It intentionally uses only the Python standard library and writes to
build/agent-harness by default so generated outputs stay out of committed source
unless a later promotion explicitly checks them in as evidence.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "examples/agent-harness/recent-repo-activity-report.example.json"
DEFAULT_OUTPUT_DIR = ROOT / "build/agent-harness"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def status_for_score(score: int) -> str:
    if score >= 80:
        return "green"
    if score >= 55:
        return "yellow"
    return "red"


def build_scoreboard(report: dict[str, Any]) -> dict[str, Any]:
    activities = report.get("activities", [])
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for activity in activities:
        grouped[activity["repo"]].append(activity)

    scores = []
    for repo in sorted(grouped):
        repo_activities = grouped[repo]
        follow_up_count = sum(1 for item in repo_activities if item.get("followUpRequired"))
        evidence_refs = [item["evidenceRef"] for item in repo_activities]
        base = 60
        evidence_bonus = min(25, len(evidence_refs) * 5)
        follow_up_penalty = min(30, follow_up_count * 10)
        score = max(0, min(100, base + evidence_bonus - follow_up_penalty))
        scores.append(
            {
                "subjectRef": f"github://{repo}",
                "score": score,
                "status": status_for_score(score),
                "evidenceRefs": evidence_refs,
                "blockedBy": ["follow-up required"] if follow_up_count else [],
                "nextAction": (
                    "Resolve follow-up items and attach validated evidence."
                    if follow_up_count
                    else "Maintain evidence cadence and keep scoreboard feed current."
                ),
            }
        )

    return {
        "schemaVersion": "v0.1",
        "snapshotId": f"scoreboard-agent-harness-{report['reportId']}",
        "generatedAt": report["generatedAt"],
        "scoreboardType": "agent-harness",
        "period": {
            "start": f"window-{report['windowDays']}-days-before-{report['generatedAt']}",
            "end": report["generatedAt"],
        },
        "scores": scores,
        "summary": "Generated from recent repository activity report.",
    }


def build_metric_event(report: dict[str, Any]) -> dict[str, Any]:
    activities = report.get("activities", [])
    repos = sorted({item["repo"] for item in activities})
    return {
        "schemaVersion": "v0.1",
        "metricEventId": f"metric-activity-count-{report['reportId']}",
        "observedAt": report["generatedAt"],
        "repo": "cross-estate",
        "workItemRef": "agent-harness-absorption-baseline",
        "outcomeRef": "outcome-governed-agent-harness",
        "metricFamily": "throughput",
        "metricName": "recent-activity-repo-count",
        "value": len(repos),
        "unit": "repositories",
        "direction": "higher-is-better",
        "evidenceRef": f"recent-repo-activity-report://{report['reportId']}",
        "notes": "Counts unique repositories represented in the recent activity report.",
    }


def build_customer_proof(report: dict[str, Any], scoreboard: dict[str, Any]) -> dict[str, Any]:
    repos = [score["subjectRef"] for score in scoreboard.get("scores", [])]
    follow_up = [
        item["repo"]
        for item in report.get("activities", [])
        if item.get("followUpRequired")
    ]
    return {
        "schemaVersion": "v0.1",
        "readoutId": f"customer-proof-{report['reportId']}",
        "generatedAt": report["generatedAt"],
        "audience": "customer-safe",
        "outcomeRef": "outcome-governed-agent-harness",
        "customerRef": "internal-reference-customer",
        "workPerformed": [
            "Generated a cross-estate activity scoreboard from repository evidence.",
            "Projected recent activity into Delivery Excellence management artifacts.",
            "Separated customer-safe readout data from raw runtime payloads.",
        ],
        "artifactsChanged": [
            "build/agent-harness/scoreboard-snapshot.generated.json",
            "build/agent-harness/delivery-metric-event.generated.json",
            "build/agent-harness/customer-proof-readout.generated.json",
        ],
        "approvals": [],
        "valueClaims": [
            f"Recent activity covers {len(repos)} repositories.",
            "Follow-up work is visible without exposing sensitive runtime details.",
        ],
        "costSummary": "Generator records no model or external service cost.",
        "evidenceRefs": repos,
        "knownLimits": [
            "Generated from the provided recent activity report only.",
            "Does not query GitHub directly; live ingestion belongs in a later automation tranche.",
        ] + ([f"Follow-up required for: {', '.join(sorted(set(follow_up)))}"] if follow_up else []),
        "nextDecision": "Wire live GitHub activity ingestion and publish recurring scoreboard snapshots.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    report = load_json(args.input)
    scoreboard = build_scoreboard(report)
    metric_event = build_metric_event(report)
    customer_proof = build_customer_proof(report, scoreboard)

    write_json(args.output_dir / "scoreboard-snapshot.generated.json", scoreboard)
    write_json(args.output_dir / "delivery-metric-event.generated.json", metric_event)
    write_json(args.output_dir / "customer-proof-readout.generated.json", customer_proof)

    print(f"wrote: {args.output_dir / 'scoreboard-snapshot.generated.json'}")
    print(f"wrote: {args.output_dir / 'delivery-metric-event.generated.json'}")
    print(f"wrote: {args.output_dir / 'customer-proof-readout.generated.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
