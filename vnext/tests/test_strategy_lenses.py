import pytest

from strategy_lenses import (
    BALANCED,
    CONTENDER,
    REBUILDER,
    StrategyLens,
    aggregate_forecast,
    contribution_breakdown,
    strategy_values,
)


def test_default_profiles_sum_to_one_and_remain_near_term_anchored():
    for lens in (CONTENDER, BALANCED, REBUILDER):
        assert sum(lens.horizon_weights) == pytest.approx(1.0)
        assert lens.horizon_weights[0] >= lens.horizon_weights[-1]

    assert CONTENDER.horizon_weights[0] > BALANCED.horizon_weights[0] > REBUILDER.horizon_weights[0]
    assert REBUILDER.horizon_weights[-1] > BALANCED.horizon_weights[-1] > CONTENDER.horizon_weights[-1]


def test_same_forecast_vector_produces_all_three_views():
    expected = [100, 95, 90, 85, 80]
    uncertainty = [10, 12, 14, 16, 18]
    values = strategy_values(expected, uncertainty)

    assert set(values) == {"balanced", "contender", "rebuilder"}
    assert values["contender"] > values["balanced"] > values["rebuilder"]


def test_rebuilder_can_prefer_later_development_without_youth_bonus():
    immediate = [100, 90, 80, 70, 60]
    developing = [70, 80, 90, 100, 110]
    no_uncertainty = [0, 0, 0, 0, 0]

    assert aggregate_forecast(immediate, no_uncertainty, CONTENDER) > aggregate_forecast(
        developing, no_uncertainty, CONTENDER
    )
    assert aggregate_forecast(developing, no_uncertainty, REBUILDER) > aggregate_forecast(
        immediate, no_uncertainty, REBUILDER
    )


def test_risk_penalty_is_explicit_and_strategy_specific():
    expected = [100, 100, 100, 100, 100]
    low_risk = [0, 0, 0, 0, 0]
    high_risk = [20, 20, 20, 20, 20]

    assert aggregate_forecast(expected, high_risk, CONTENDER) == pytest.approx(93.0)
    assert aggregate_forecast(expected, high_risk, BALANCED) == pytest.approx(95.0)
    assert aggregate_forecast(expected, high_risk, REBUILDER) == pytest.approx(96.4)
    assert aggregate_forecast(expected, low_risk, CONTENDER) == pytest.approx(100.0)


def test_breakdown_reconciles_exactly_to_total():
    expected = [100, 95, 90, 85, 80]
    uncertainty = [10, 12, 14, 16, 18]
    rows = contribution_breakdown(expected, uncertainty, BALANCED)

    assert sum(row["contribution"] for row in rows) == pytest.approx(
        aggregate_forecast(expected, uncertainty, BALANCED)
    )


def test_invalid_profile_and_forecast_shapes_fail():
    with pytest.raises(ValueError, match="sum to one"):
        StrategyLens("bad", (0.5, 0.4), 0.2)

    with pytest.raises(ValueError, match="length"):
        aggregate_forecast([100], [10], BALANCED)

    with pytest.raises(ValueError, match="uncertainty length"):
        aggregate_forecast([1, 2, 3, 4, 5], [1], BALANCED)
