from roster_cut_optimiser import optimise_retained_roster
from roster_optimiser import PlayerUtility, RosterSlot


def player(player_id, utility, positions):
    return PlayerUtility(player_id, utility, frozenset(positions))


def slot(slot_id, positions):
    return RosterSlot(slot_id, frozenset(positions))


def test_cuts_lowest_utility_when_lineup_remains_feasible():
    players = [
        player("mid_a", 100, {"MID"}),
        player("mid_b", 90, {"MID"}),
        player("fwd_a", 80, {"GFWD"}),
        player("fwd_b", 70, {"GFWD"}),
        player("depth", 10, {"MID"}),
    ]
    slots = [slot("MID-1", {"MID"}), slot("GFWD-1", {"GFWD"})]

    result = optimise_retained_roster(players, slots, retain_limit=4)

    assert result.cut_player_ids == frozenset({"depth"})
    assert len(result.retained_player_ids) == 4
    assert len(result.lineup_player_ids) == 2


def test_positional_constraint_can_override_naive_lowest_cut():
    players = [
        player("mid_100", 100, {"MID"}),
        player("mid_90", 90, {"MID"}),
        player("mid_80", 80, {"MID"}),
        player("forward_20", 20, {"GFWD"}),
        player("forward_10", 10, {"GFWD"}),
    ]
    slots = [slot("MID-1", {"MID"}), slot("GFWD-1", {"GFWD"})]

    result = optimise_retained_roster(players, slots, retain_limit=3)

    assert "forward_20" in result.retained_player_ids
    assert result.cut_player_ids == frozenset({"mid_80", "forward_10"})


def test_dual_position_player_can_protect_roster_flexibility():
    players = [
        player("dual", 60, {"MID", "GFWD"}),
        player("mid", 100, {"MID"}),
        player("forward", 90, {"GFWD"}),
        player("extra_mid", 70, {"MID"}),
    ]
    slots = [slot("MID-1", {"MID"}), slot("GFWD-1", {"GFWD"})]

    result = optimise_retained_roster(players, slots, retain_limit=3)

    assert result.cut_player_ids == frozenset({"dual"})
    assert len(result.lineup_player_ids) == 2


def test_roster_at_or_below_limit_is_unchanged():
    players = [player("mid", 100, {"MID"}), player("forward", 90, {"GFWD"})]
    result = optimise_retained_roster(players, [slot("MID-1", {"MID"})], retain_limit=40)

    assert result.cut_player_ids == frozenset()
    assert result.retained_player_ids == frozenset({"mid", "forward"})


def test_infeasible_post_cut_roster_fails():
    players = [
        player("mid_a", 100, {"MID"}),
        player("mid_b", 90, {"MID"}),
        player("forward", 80, {"GFWD"}),
    ]
    slots = [slot("MID-1", {"MID"}), slot("GFWD-1", {"GFWD"})]

    try:
        optimise_retained_roster(players, slots, retain_limit=1)
    except ValueError as exc:
        assert "smaller than" in str(exc)
    else:
        raise AssertionError("expected retain limit below lineup size to fail")
