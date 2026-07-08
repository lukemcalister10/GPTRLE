from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

FORWARD_FIELDS = ("vP1", "vP2")
FLOOR = 1.0


def apply_forward_floor(
    payload: dict[str, Any],
    authoritative_keys: set[str] | None = None,
    floor: float = FLOOR,
) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Any]]:
    if not math.isfinite(floor) or floor <= 0:
        raise ValueError("floor must be finite and positive")
    active = payload.get("active")
    if not isinstance(active, list) or not active:
        raise ValueError("payload must contain a non-empty active list")

    output = copy.deepcopy(payload)
    rows = output["active"]
    keys = [str(row.get("key") or "") for row in rows]
    if any(not key for key in keys) or len(keys) != len(set(keys)):
        raise ValueError("active rows require unique non-empty legacy keys")
    board_keys = set(keys)
    authoritative = board_keys if authoritative_keys is None else {str(key) for key in authoritative_keys}
    missing = sorted(authoritative - board_keys)
    if missing:
        raise ValueError(f"authoritative keys missing from board: {missing[:10]}")

    changes: list[dict[str, Any]] = []
    for row in rows:
        key = str(row["key"])
        for field in FORWARD_FIELDS:
            if field not in row:
                raise ValueError(f"{key} missing required field {field}")
            try:
                value = float(row[field])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{key} {field} is not numeric") from exc
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{key} {field} must be finite and non-negative")
            if value == 0.0:
                row[field] = floor
                changes.append(
                    {
                        "key": key,
                        "name": str(row.get("name") or ""),
                        "field": field,
                        "old_value": 0.0,
                        "new_value": float(floor),
                        "authoritative": key in authoritative,
                        "legacy_only": key not in authoritative,
                    }
                )

    change_frame = pd.DataFrame(
        changes,
        columns=[
            "key",
            "name",
            "field",
            "old_value",
            "new_value",
            "authoritative",
            "legacy_only",
        ],
    )

    original_by_key = {str(row["key"]): row for row in active}
    candidate_by_key = {str(row["key"]): row for row in rows}
    if list(original_by_key) != list(candidate_by_key):
        raise ValueError("player order changed")
    changed_pairs = set(zip(change_frame.get("key", []), change_frame.get("field", [])))
    for key in original_by_key:
        before = original_by_key[key]
        after = candidate_by_key[key]
        if set(before) != set(after):
            raise ValueError(f"field set changed for {key}")
        for field in before:
            if (key, field) in changed_pairs:
                continue
            if before[field] != after[field]:
                raise ValueError(f"unexpected change for {key} field {field}")

    remaining_authoritative_zeros = 0
    for row in rows:
        if str(row["key"]) not in authoritative:
            continue
        remaining_authoritative_zeros += sum(float(row[field]) == 0.0 for field in FORWARD_FIELDS)

    affected_authoritative = change_frame.loc[
        change_frame["authoritative"], "key"
    ].nunique() if len(change_frame) else 0
    summary = {
        "status": "continuity_candidate_complete",
        "raw_active_players": len(rows),
        "authoritative_players": len(authoritative),
        "legacy_only_players": len(board_keys - authoritative),
        "floor": float(floor),
        "forward_fields": list(FORWARD_FIELDS),
        "changed_fields": int(len(change_frame)),
        "changed_authoritative_fields": int(change_frame["authoritative"].sum()) if len(change_frame) else 0,
        "changed_legacy_only_fields": int(change_frame["legacy_only"].sum()) if len(change_frame) else 0,
        "affected_authoritative_players": int(affected_authoritative),
        "remaining_authoritative_exact_zeros": int(remaining_authoritative_zeros),
        "current_values_changed": 0,
        "ranks_changed": 0,
        "non_zero_forward_values_changed": 0,
        "notes": {
            "scope": "exact zeros in vP1 and vP2 only",
            "task006": "not used or promoted",
            "production": "candidate adapter only; frozen Claude export remains unchanged",
        },
    }
    return output, change_frame, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=Path, required=True)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--floor", type=float, default=FLOOR)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    payload = json.loads(args.board.read_text())
    authoritative_keys = None
    if args.registry is not None:
        registry = pd.read_csv(args.registry)
        if "legacy_key" not in registry or registry["legacy_key"].isna().any():
            raise ValueError("registry must contain non-null legacy_key")
        if registry["legacy_key"].duplicated().any():
            raise ValueError("registry legacy_key must be unique")
        authoritative_keys = set(registry["legacy_key"].astype(str))

    candidate, changes, summary = apply_forward_floor(payload, authoritative_keys, args.floor)
    (args.out / "candidate_board.json").write_text(
        json.dumps(candidate, separators=(",", ":"), allow_nan=False) + "\n"
    )
    changes.to_csv(args.out / "forward_zero_changes.csv", index=False)
    (args.out / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
