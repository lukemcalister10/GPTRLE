"""Tests for reviewed historical eligibility."""
from pathlib import Path

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
