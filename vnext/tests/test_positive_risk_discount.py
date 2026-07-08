import math

import pytest

from positive_risk_discount import aggregate_positive_risk, discount_expected_utility
from strategy_lenses import CONTENDER


def test_zero_uncertainty_preserves_mean():
    assert discount_expected_utility(100, 0, risk_aversion=0.35) == 100


def test_higher_uncertainty_reduces_value_without_crossing_negative():
    low = discount_expected_utility(100, 20, risk_aversion=0.35)
    high = discount_expected_utility(100, 200, risk_aversion=0.35)

    assert 0 < high < low < 100


def test_zero_expected_utility_remains_zero():
    assert discount_expected_utility(0, 100, risk_aversion=0.35) == 0


def test_small_uncertainty_approximates_linear_penalty():
    mean = 1000.0
    spread = 10.0
    risk = 0.25
    exponential = discount_expected_utility(mean, spread, risk_aversion=risk)
    linear = mean - risk * spread

    assert exponential == pytest.approx(linear, rel=5e-6)


def test_aggregation_is_weighted_and_positive():
    value = aggregate_positive_risk(
        [100, 80, 60, 40, 20],
        [20, 20, 20, 20, 20],
        CONTENDER,
    )

    assert value > 0
    assert value < sum(w * m for w, m in zip(CONTENDER.horizon_weights, [100, 80, 60, 40, 20]))


def test_invalid_inputs_fail():
    for args in [
        (-1, 1, 0.2),
        (1, -1, 0.2),
        (1, 1, -0.2),
        (math.inf, 1, 0.2),
    ]:
        with pytest.raises(ValueError):
            discount_expected_utility(args[0], args[1], risk_aversion=args[2])
