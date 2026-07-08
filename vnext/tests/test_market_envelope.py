import pytest

from market_envelope import (
    MarketEnvelopePolicy,
    StrategyValues,
    market_value,
    trade_opportunity,
)


def test_market_value_uses_two_strongest_strategy_values():
    values = StrategyValues(contender=100, balanced=80, rebuilder=40)
    assert market_value(values) == pytest.approx(94)


def test_rebuilder_asset_can_have_market_value_above_contender_fit():
    values = StrategyValues(contender=30, balanced=60, rebuilder=100)
    result = trade_opportunity(values, current_roster_value=20)

    assert result.market_value == pytest.approx(88)
    assert result.gross_surplus == pytest.approx(68)
    assert result.realisable_trade_opportunity == pytest.approx(51)


def test_elite_current_producer_on_rebuilder_can_open_trade_line():
    values = StrategyValues(contender=120, balanced=90, rebuilder=55)
    result = trade_opportunity(values, current_roster_value=40)

    assert result.market_value == pytest.approx(111)
    assert result.realisable_trade_opportunity > 0


def test_no_trade_surplus_when_current_roster_is_best_use():
    values = StrategyValues(contender=100, balanced=90, rebuilder=70)
    result = trade_opportunity(values, current_roster_value=110)

    assert result.gross_surplus == 0
    assert result.realisable_trade_opportunity == 0


def test_liquidity_haircut_is_explicit_and_replaceable():
    policy = MarketEnvelopePolicy(
        best_use_weight=0.5,
        second_best_use_weight=0.5,
        liquidity=0.4,
    )
    result = trade_opportunity(
        StrategyValues(contender=100, balanced=80, rebuilder=20),
        current_roster_value=50,
        policy=policy,
    )

    assert result.market_value == 90
    assert result.gross_surplus == 40
    assert result.realisable_trade_opportunity == 16


def test_invalid_policy_fails():
    with pytest.raises(ValueError, match="sum to one"):
        MarketEnvelopePolicy(0.8, 0.3, 0.5)

    with pytest.raises(ValueError, match="cannot exceed one"):
        MarketEnvelopePolicy(0.7, 0.3, 1.1)
