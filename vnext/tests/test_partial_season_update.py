import pytest

from partial_season_update import PartialSeasonPolicy, update_partial_season


def test_short_strong_scoring_sample_updates_but_remains_shrunk():
    result = update_partial_season(
        prior_scoring_rate=80,
        observed_scoring_rate=100,
        prior_availability_rate=0.8,
        games_played=4,
        rounds_observed=14,
    )

    assert result.scoring_credibility == pytest.approx(4 / 12)
    assert result.updated_scoring_rate == pytest.approx(86.6666666667)
    assert result.updated_scoring_rate < 100


def test_twelve_of_twenty_four_negative_availability_uses_about_thirty_five_percent_weight():
    result = update_partial_season(
        prior_scoring_rate=90,
        observed_scoring_rate=90,
        prior_availability_rate=1.0,
        games_played=12,
        rounds_observed=24,
    )

    assert result.observed_availability_rate == 0.5
    assert result.availability_credibility == pytest.approx(12 / 34)
    assert result.availability_credibility == pytest.approx(0.3529411765)
    assert result.updated_availability_rate == pytest.approx(0.8235294118)


def test_negative_availability_evidence_is_less_than_direct_proportional_weight():
    result = update_partial_season(
        prior_scoring_rate=90,
        observed_scoring_rate=90,
        prior_availability_rate=1.0,
        games_played=12,
        rounds_observed=24,
    )

    assert result.availability_credibility < 0.5


def test_positive_availability_evidence_updates_faster_than_negative_deficit():
    positive = update_partial_season(
        prior_scoring_rate=80,
        observed_scoring_rate=80,
        prior_availability_rate=0.5,
        games_played=12,
        rounds_observed=14,
    )
    negative = update_partial_season(
        prior_scoring_rate=80,
        observed_scoring_rate=80,
        prior_availability_rate=1.0,
        games_played=7,
        rounds_observed=14,
    )

    assert positive.availability_credibility > negative.availability_credibility


def test_zero_games_preserves_scoring_prior_and_updates_availability_only():
    result = update_partial_season(
        prior_scoring_rate=75,
        observed_scoring_rate=None,
        prior_availability_rate=0.5,
        games_played=0,
        rounds_observed=14,
    )

    assert result.scoring_credibility == 0
    assert result.updated_scoring_rate == 75
    assert result.updated_availability_rate < 0.5
    assert result.updated_availability_rate > 0


def test_more_games_increase_scoring_credibility():
    four = update_partial_season(
        prior_scoring_rate=80,
        observed_scoring_rate=100,
        prior_availability_rate=0.8,
        games_played=4,
        rounds_observed=14,
    )
    twelve = update_partial_season(
        prior_scoring_rate=80,
        observed_scoring_rate=100,
        prior_availability_rate=0.8,
        games_played=12,
        rounds_observed=14,
    )

    assert twelve.scoring_credibility > four.scoring_credibility
    assert twelve.updated_scoring_rate > four.updated_scoring_rate


def test_policy_is_explicit_and_replaceable():
    stronger_prior = PartialSeasonPolicy(
        scoring_prior_games=16,
        positive_availability_prior_rounds=8,
        negative_availability_prior_deficit=22,
    )
    result = update_partial_season(
        prior_scoring_rate=80,
        observed_scoring_rate=100,
        prior_availability_rate=0.8,
        games_played=4,
        rounds_observed=14,
        policy=stronger_prior,
    )

    assert result.scoring_credibility == pytest.approx(0.2)
    assert result.updated_scoring_rate == pytest.approx(84)


def test_invalid_exposure_fails():
    with pytest.raises(ValueError, match="between zero and rounds_observed"):
        update_partial_season(
            prior_scoring_rate=80,
            observed_scoring_rate=90,
            prior_availability_rate=0.8,
            games_played=15,
            rounds_observed=14,
        )

    with pytest.raises(ValueError, match="required"):
        update_partial_season(
            prior_scoring_rate=80,
            observed_scoring_rate=None,
            prior_availability_rate=0.8,
            games_played=4,
            rounds_observed=14,
        )
