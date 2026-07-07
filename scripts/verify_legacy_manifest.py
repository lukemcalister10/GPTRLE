#!/usr/bin/env python3
"""Verify that critical legacy production files have not changed unexpectedly."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "artifacts" / "legacy_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    for relative, expected in data["files"].items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"MISSING {relative}")
            continue
        actual = sha256(path)
        if actual != expected:
            failures.append(f"CHANGED {relative}\n  expected {expected}\n  actual   {actual}")
    if failures:
        print("Legacy manifest verification FAILED:\n" + "\n".join(failures))
        return 1
    print(f"Legacy manifest verification passed: {len(data['files'])} files unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
