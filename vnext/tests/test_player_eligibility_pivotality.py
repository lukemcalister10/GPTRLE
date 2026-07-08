from league_config import ALL_POSITIONS
from player_eligibility_pivotality import eligibility_pivotality
from roster_optimiser import PlayerUtility, RosterSlot


def player(player_id, utility, positions):
    return PlayerUtility(player_id, utility, frozenset(positions))


def slot(slot_id, positions):
    return RosterSlot(slot_id, frozenset(positions))


def test_blocking_pivotal_position_loses_league_utility_but_preserves_free_slot_access():
    players = [
        player("key_def", 80, {"KDEF"}),
        player("replacement_key_def", 10, {"KDEF"}),
        player("mid_100", 100, {"MID"}),
        player("mid_90", 90, {"MID"}),
    ]
    slots = [
        slot("KDEF-1", {"KDEF"}),
        RosterSlot("FREE-1", ALL_POSITIONS),
    ]

    result = eligibility_pivotality(
        players,
        slots,
        player_id="key_def",
        blocked_positions=frozenset({"KDEF"}),
    )

    assert result.league_utility_loss == 70


def test_nonbinding_eligibility_has_zero_pivotality():
    players = [
        player("dual", 100, {"MID", "GFWD"}),
        player("mid", 90, {"MID"}),
        player("forward", 80, {"GFWD"}),
    ]
    slots = [
        slot("MID-1", {"MID"}),
        RosterSlot("FREE-1", ALL_POSITIONS),
    ]

    result = eligibility_pivotality(
        players,
        slots,
        player_id="dual",
        blocked_positions=frozenset({"GFWD"}),
    )

    assert result.league_utility_loss == 0


def test_blocking_one_position_preserves_other_current_eligibility():
    players = [
        player("dual", 100, {"KDEF", "GDEF"}),
        player("general", 90, {"GDEF"}),
        player("mid", 80, {"MID"}),
    ]
    slots = [
        slot("GDEF-1", {"GDEF"}),
        RosterSlot("FREE-1", ALL_POSITIONS),
    ]

    result = eligibility_pivotality(
        players,
        slots,
        player_id="dual",
        blocked_positions=frozenset({"KDEF"}),
    )

    assert result.league_utility_loss == 0


def test_unknown_or_irrelevant_player_position_behaviour():
    players = [player("mid", 100, {"MID"})]
    slots = [RosterSlot("FREE-1", ALL_POSITIONS)]

    assert eligibility_pivotality(
        players,
        slots,
        player_id="mid",
        blocked_positions=frozenset({"KDEF"}),
    ).league_utility_loss == 0

    try:
        eligibility_pivotality(
            players,
            slots,
            player_id="missing",
            blocked_positions=frozenset({"KDEF"}),
        )
    except KeyError:
        pass
    else:
        raise AssertionError("missing player must fail")
