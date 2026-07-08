from __future__ import annotations

import pytest

from forward_value_continuity import apply_forward_floor


def _row(key: str, p1: float, p2: float) -> dict:
    return {
        "key": key,
        "name": key,
        "v": 10,
        "rank": 3,
        "vM2": 9,
        "vM1": 8,
        "vP1": p1,
        "vP2": p2,
    }


def test_only_exact_forward_zeros_are_floored() -> None:
    payload = {"active": [_row("a", 0, 0), _row("b", 2, 0), _row("legacy", 3, 4)]}
    candidate, changes, summary = apply_forward_floor(payload, {"a", "b"})

    assert summary["changed_fields"] == 3
    assert summary["affected_authoritative_players"] == 2
    assert summary["changed_legacy_only_fields"] == 0
    assert summary["remaining_authoritative_exact_zeros"] == 0
    assert candidate["active"][0]["vP1"] == 1
    assert candidate["active"][0]["vP2"] == 1
    assert candidate["active"][1]["vP1"] == 2
    assert candidate["active"][1]["vP2"] == 1
    assert candidate["active"][0]["v"] == 10
    assert candidate["active"][0]["rank"] == 3
    assert set(changes["field"]) == {"vP1", "vP2"}
    assert payload["active"][0]["vP1"] == 0


def test_invalid_or_ambiguous_boards_fail_closed() -> None:
    duplicate = {"active": [_row("a", 0, 1), _row("a", 1, 1)]}
    with pytest.raises(ValueError, match="unique"):
        apply_forward_floor(duplicate)

    negative = {"active": [_row("a", -1, 1)]}
    with pytest.raises(ValueError, match="non-negative"):
        apply_forward_floor(negative)

    missing_key = {"active": [_row("a", 0, 1)]}
    with pytest.raises(ValueError, match="missing from board"):
        apply_forward_floor(missing_key, {"a", "b"})
