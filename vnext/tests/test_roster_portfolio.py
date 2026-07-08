from roster_portfolio import (
    BALANCED_PORTFOLIO,
    CONTENDER_PORTFOLIO,
    REBUILDER_PORTFOLIO,
    PortfolioPlayer,
    PortfolioRole,
    classify_portfolio_role,
)


def player(**kwargs):
    defaults = dict(
        player_id="p",
        lineup_utility=0.0,
        emergency_utility=0.0,
        future_asset_utility=0.0,
        trade_utility=0.0,
    )
    defaults.update(kwargs)
    return PortfolioPlayer(**defaults)


def test_best_23_and_extended_core_are_core_assets():
    assert classify_portfolio_role(
        player(in_best_23=True), CONTENDER_PORTFOLIO
    ) == PortfolioRole.CORE
    assert classify_portfolio_role(
        player(in_extended_core=True), CONTENDER_PORTFOLIO
    ) == PortfolioRole.CORE


def test_valuable_non_core_contender_asset_is_trade_candidate_not_keeper_by_default():
    asset = player(
        emergency_utility=10,
        future_asset_utility=80,
        trade_utility=90,
    )

    assert classify_portfolio_role(
        asset,
        CONTENDER_PORTFOLIO,
        trade_threshold=20,
    ) == PortfolioRole.TRADE_CANDIDATE


def test_low_value_positional_cover_can_be_retained_as_emergency_depth():
    depth = player(
        emergency_utility=18,
        future_asset_utility=5,
        trade_utility=4,
        required_positional_cover=True,
    )

    assert classify_portfolio_role(
        depth,
        CONTENDER_PORTFOLIO,
        trade_threshold=20,
    ) == PortfolioRole.EMERGENCY_DEPTH


def test_rebuilder_can_hold_elite_production_as_trade_inventory():
    veteran = player(
        lineup_utility=100,
        emergency_utility=0,
        future_asset_utility=15,
        trade_utility=75,
    )

    assert classify_portfolio_role(
        veteran,
        REBUILDER_PORTFOLIO,
        trade_threshold=20,
    ) == PortfolioRole.TRADE_CANDIDATE


def test_rebuilder_can_hold_development_asset_without_immediate_points():
    prospect = player(
        lineup_utility=0,
        emergency_utility=0,
        future_asset_utility=60,
        trade_utility=5,
    )

    assert classify_portfolio_role(
        prospect,
        REBUILDER_PORTFOLIO,
        trade_threshold=20,
        development_threshold=20,
    ) == PortfolioRole.DEVELOPMENT


def test_low_value_non_core_player_is_cut_candidate():
    fringe = player(
        lineup_utility=0,
        emergency_utility=0,
        future_asset_utility=0,
        trade_utility=0,
    )

    assert classify_portfolio_role(
        fringe,
        BALANCED_PORTFOLIO,
        trade_threshold=20,
        development_threshold=20,
    ) == PortfolioRole.CUT_CANDIDATE
