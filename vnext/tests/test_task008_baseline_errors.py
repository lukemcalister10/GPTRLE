from __future__ import annotations

import math

import pytest

from audit_task008_baseline_errors import build_audit


def _player(
    key: str,
    *,
    games: int,
    value: float,
    overlay_value: float,
    pn: float,
    ped_decay: float,
    v_p1: float,
    v_p2: float,
    current_avg: float | None = None,
    h26: bool = False,
) -> dict:
    track = [] if current_avg is None else [{"s": 1, "a": current_avg}]
    return {
        "name": key,
        "key": key,
        "g": games,
        "pn": pn,
        "ps": pn,
        "ln": pn,
        "lns": pn,
        "pedDecay": ped_decay,
        "vM2": value,
        "vM1": value,
        "vP1": v_p1,
        "vP2": v_p2,
        "claudeV": value,
        "v": overlay_value,
        "claudeRank": 1,
        "rank": 1,
        "track": track,
        "h26": h26,
        "ep": 10,
    }


def test_audit_uses_unchanged_claude_value_not_task006_overlay() -> None:
    payload = {
        "active": [
            _player(
                "zero",
                games=0,
                value=100,
                overlay_value=9999,
                pn=80,
                ped_decay=1,
                v_p1=100,
                v_p2=100,
            ),
            _player(
                "established",
                games=80,
                value=50,
                overlay_value=9999,
                pn=60,
                ped_decay=0.2,
                v_p1=50,
                v_p2=50,
            ),
        ]
    }

    audit, cohorts, summary = build_audit(payload)

    assert summary["value_field"] == "claudeV"
    assert summary["zero_history_median_value"] == 100
    assert summary["established_low_ceiling_players"] == 1
    assert summary["established_below_zero_history_median"] == 1
    assert audit.loc[audit.key == "established", "claude_value"].item() == 50
    assert "all" in set(cohorts.cohort)


def test_audit_detects_partial_season_pedigree_and_exact_forward_zero() -> None:
    payload = {
        "active": [
            _player(
                "partial",
                games=60,
                value=200,
                overlay_value=200,
                pn=90,
                ped_decay=0.25,
                v_p1=0,
                v_p2=20,
                current_avg=70,
                h26=True,
            )
        ]
    }

    audit, _, summary = build_audit(payload)
    row = audit.iloc[0]

    assert bool(row.partial_season_observed)
    assert row.pn_error_vs_current == pytest.approx(20)
    assert bool(row.pedigree_persistence)
    assert bool(row.pathological_zero_value)
    assert summary["partial_season_observed_players"] == 1
    assert summary["pathological_forward_zero_players"] == 1


def test_audit_fails_closed_on_duplicate_keys_and_missing_fields() -> None:
    player = _player(
        "duplicate",
        games=0,
        value=10,
        overlay_value=10,
        pn=10,
        ped_decay=0,
        v_p1=10,
        v_p2=10,
    )
    with pytest.raises(ValueError, match="unique"):
        build_audit({"active": [player, dict(player)]})

    malformed = dict(player)
    malformed.pop("vP2")
    with pytest.raises(ValueError, match="missing required"):
        build_audit({"active": [malformed]})


def test_audit_flags_non_finite_values() -> None:
    payload = {
        "active": [
            _player(
                "bad",
                games=20,
                value=math.nan,
                overlay_value=10,
                pn=50,
                ped_decay=0,
                v_p1=10,
                v_p2=10,
            ),
            _player(
                "finite-zero-history",
                games=0,
                value=20,
                overlay_value=20,
                pn=50,
                ped_decay=1,
                v_p1=20,
                v_p2=20,
            ),
        ]
    }
    audit, _, summary = build_audit(payload)
    assert bool(audit.iloc[0].non_finite_value)
    assert summary["non_finite_value_players"] == 1


def test_authoritative_registry_excludes_legacy_only_from_metrics() -> None:
    payload = {
        "active": [
            _player(
                "authoritative",
                games=80,
                value=50,
                overlay_value=50,
                pn=60,
                ped_decay=0,
                v_p1=50,
                v_p2=50,
            ),
            _player(
                "legacy-only",
                games=80,
                value=40,
                overlay_value=40,
                pn=60,
                ped_decay=0,
                v_p1=40,
                v_p2=40,
            ),
            _player(
                "zero",
                games=0,
                value=100,
                overlay_value=100,
                pn=80,
                ped_decay=1,
                v_p1=100,
                v_p2=100,
            ),
        ]
    }

    audit, cohorts, summary = build_audit(payload, {"authoritative", "zero"})

    assert summary["raw_active_players"] == 3
    assert summary["players"] == 2
    assert summary["legacy_only_keys"] == ["legacy-only"]
    assert summary["established_below_zero_history_median"] == 1
    assert int(cohorts.loc[cohorts.cohort == "all", "players"].item()) == 2
    assert bool(audit.loc[audit.key == "legacy-only", "legacy_only"].item())
