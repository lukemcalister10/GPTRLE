"""Tests for reviewed historical eligibility."""
import json
from pathlib import Path

from benchmark import LOCKED_FOLDS
from build_historical_cohorts import build_locked_cohorts
from historical_eligibility import DraftGuruEligibilityResolver


def test_resolver_has_complete_reviewed_matrix():
    resolver = DraftGuruEligibilityResolver()
    assert len(resolver.database_keys) == 2652
    assert len(resolver.matrix) == 18564
    assert resolver.matrix["eligible"].eq("True").sum() == 5622
    assert resolver.matrix["eligible"].eq("False").sum() == 12942
    assert resolver.matrix.groupby("player_key")["origin_year"].nunique().eq(7).all()


def test_reviewed_duplicate_identities_remain_separate():
    resolver = DraftGuruEligibilityResolver()
    evidence = resolver.evidence_frame()
    slugs = evidence.loc[evidence["eligible"], ["player_key", "draftguru_player_slug"]].drop_duplicates()
    by_slug = dict(zip(slugs["draftguru_player_slug"], slugs["player_key"]))
    assert by_slug["will_hayes/1"] == "will-hayes-a"
    assert by_slug["bailey_williams/1"] == "bailey-williams-wb"
    assert by_slug["bailey_williams/2"] == "bailey-williams-wc"
    assert by_slug["callum_brown/1"] == "callum-brown"
    assert by_slug["callum_brown/2"] == "callum-brown-ire"
    assert by_slug["josh_kennedy/1"] == "joshua-kennedy"
    assert by_slug["josh_kennedy/2"] == "josh-p-kennedy"
    assert by_slug["sam_reid/2"] == "samuel-reid"
    assert by_slug["sam_reid/3"] == "sam-reid-syd"


def test_resolver_uses_only_key_and_origin():
    resolver = DraftGuruEligibilityResolver()
    base = {"key": "will-hayes-a"}
    mutated = {
        "key": "will-hayes-a",
        "_retired": True,
        "_club": "Injected Club",
        "present_position": "RUCK",
        "future_position": "RUCK",
        "scoring": [{"year": 2026, "avg": 200, "games": 23}],
    }
    assert resolver(base, 2019) == resolver(mutated, 2019)
    assert resolver(base, 2019).eligible is True
    assert resolver(base, 2018).eligible is False


def test_locked_cohort_artifacts_are_complete_and_deterministic(tmp_path: Path):
    first = build_locked_cohorts(tmp_path / "first")
    second = build_locked_cohorts(tmp_path / "second")
    assert first == second
    assert first["database_unique_keys"] == 2652
    assert first["target_failure_rows"] == 0
    assert first["identity_exclusion_rows"] == 76

    resolver = DraftGuruEligibilityResolver()
    evidence = resolver.evidence_frame()
    expected_targets = 0
    for origins in LOCKED_FOLDS.values():
        for origin in origins:
            expected_targets += int(
                ((evidence["origin_year"] == origin) & evidence["eligible"]).sum()
            )
    assert first["target_rows"] == expected_targets

    manifest = json.loads((tmp_path / "first" / "manifest.json").read_text())
    assert manifest == json.loads(json.dumps(first))
    assert set(first["artifacts"]) == {
        "fold_plan.csv",
        "included_snapshots.csv",
        "cohort_membership.csv",
        "targets.csv",
        "excluded.csv",
        "target_failures.csv",
        "cohort_counts.csv",
        "exclusion_counts.csv",
        "identity_exclusions.csv",
    }
