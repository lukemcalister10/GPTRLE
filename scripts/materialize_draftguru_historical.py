#!/usr/bin/env python3
"""Materialise and verify committed DraftGuru historical eligibility sources."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "historical"
FILES = (
    "historical_eligibility_2018_2024.csv",
    "draftguru_player_key_map_final.csv",
    "draftguru_players_excluded_from_repository_mapping.csv",
    "database_player_keys.csv",
)


def decode_source(path: Path) -> bytes:
    encoded = "".join(path.read_text(encoding="ascii").split())
    return gzip.decompress(base64.b64decode(encoded, validate=True))


def materialize(source_dir: Path, output_dir: Path, *, write: bool = True) -> dict[str, str]:
    manifest = json.loads((source_dir / "final_manifest.json").read_text(encoding="utf-8"))
    expected = manifest["files"]
    output_dir.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}

    for name in FILES:
        source_path = source_dir / f"{name}.gz.b64"
        raw = decode_source(source_path)
        digest = hashlib.sha256(raw).hexdigest()
        expected_digest = expected[name]["sha256"]
        expected_bytes = int(expected[name]["bytes"])
        if digest != expected_digest:
            raise ValueError(f"hash mismatch for {name}: {digest} != {expected_digest}")
        if len(raw) != expected_bytes:
            raise ValueError(f"byte-count mismatch for {name}: {len(raw)} != {expected_bytes}")
        hashes[name] = digest
        if write:
            (output_dir / name).write_bytes(raw)

    return hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    hashes = materialize(args.source_dir, args.output_dir, write=not args.check_only)
    for name, digest in hashes.items():
        print(f"{digest}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
