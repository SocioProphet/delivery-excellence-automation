#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANDIDATE_CHECKS = [
    [sys.executable, str(ROOT / "scripts" / "validate_configs.py")],
    [sys.executable, str(ROOT / "scripts" / "validate_all_contracts.py")],
    [sys.executable, str(ROOT / "scripts" / "validate_metadata_operations.py")],
    [sys.executable, str(ROOT / "scripts" / "validate_service_catalog_and_sla.py")],
    [sys.executable, str(ROOT / "scripts" / "validate_payout_objects.py")],
    [sys.executable, str(ROOT / "scripts" / "validate_incentive_policy.py")],
    [sys.executable, str(ROOT / "scripts" / "validate_professional_intelligence.py")],
]


def main() -> int:
    failures = 0
    skipped = 0

    for cmd in CANDIDATE_CHECKS:
        script = Path(cmd[-1])
        if not script.exists():
            print(f"[SKIP] missing {script.relative_to(ROOT)}")
            skipped += 1
            continue
        print(f"[RUN] {' '.join(str(part) for part in cmd)}")
        result = subprocess.run(cmd, cwd=ROOT, check=False)
        if result.returncode != 0:
            failures += 1
            print(f"[FAIL] {script.relative_to(ROOT)} exited with {result.returncode}")
        else:
            print(f"[OK] {script.relative_to(ROOT)}")

    if failures:
        print(f"[FAIL] validation suite completed with {failures} failed check(s) and {skipped} skipped check(s)")
        return 1

    print(f"[OK] validation suite completed with {skipped} skipped check(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
