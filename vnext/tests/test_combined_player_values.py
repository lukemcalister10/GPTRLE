from combined_player_values import combine_player_values, rank_combined_players
from player_comparison import PlayerComparison


def test_combines_intrinsic_and_scarcity_by_lens():
    players = [PlayerComparison("a", 100, 90, 80)]
    combined = combine_player_values(
        players,
        {
            "contender": {"a": 5},
            "balanced": {"a": 3},
            "rebuilder": {"a": 2},
        },
    )[0]

    assert combined.contender_value == 105
    assert combined.balanced_value == 93
    assert combined.rebuilder_value == 82


def test_missing_premium_defaults_to_zero():
    players = [
        PlayerComparison("a", 100, 90, 80),
        PlayerComparison("b", 95, 85, 75),
    ]
    combined = combine_player_values(
        players,
        {
            "contender": {"a": 5},
            "balanced": {},
            "rebuilder": {},
        },
    )
    by_id = {row.player_id: row for row in combined}

    assert by_id["b"].contender_scarcity == 0
    assert by_id["b"].contender_value == 95


def test_scarcity_can_change_close_rank_but_not_intrinsic_components():
    players = [
        PlayerComparison("a", 100, 100, 100),
        PlayerComparison("b", 99, 99, 99),
    ]
    combined = combine_player_values(
        players,
        {
            "contender": {"b": 2},
            "balanced": {},
            "rebuilder": {},
        },
    )

    assert [row.player_id for row in rank_combined_players(combined, lens="contender")] == [
        "b",
        "a",
    ]
    by_id = {row.player_id: row for row in combined}
    assert by_id["b"].contender_intrinsic == 99


def test_unknown_player_or_invalid_lens_fails():
    players = [PlayerComparison("a", 100, 90, 80)]

    try:
        combine_player_values(
            players,
            {
                "contender": {"missing": 1},
                "balanced": {},
                "rebuilder": {},
            },
        )
    except ValueError as exc:
        assert "unknown" in str(exc)
    else:
        raise AssertionError("unknown premium player must fail")

    combined = combine_player_values(
        players,
        {"contender": {}, "balanced": {}, "rebuilder": {}},
    )
    try:
        rank_combined_players(combined, lens="specific_team")
    except KeyError:
        pass
    else:
        raise AssertionError("invalid lens must fail")
