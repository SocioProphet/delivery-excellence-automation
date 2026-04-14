#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    [sys.executable, str(ROOT / "scripts" / "validate_agentic_contracts.py")],
    [sys.executable, str(ROOT / "scripts" / "validate_engagement_objects.py")],
]


def main() -> int:
    failures = 0
    for cmd in CHECKS:
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            failures += 1
    if failures:
        return 1
    print("[OK] all contract validations passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
