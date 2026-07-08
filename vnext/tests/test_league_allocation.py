from league_allocation import (
    assigned_position_summary,
    build_league_active_slots,
    build_league_scoring_slots,
    league_flexibility_value,
    marginal_league_utility,
    optimise_league_active_lineups,
)
from roster_optimiser import PlayerUtility, RosterSlot, optimise_roster


def player(player_id, utility, positions, primary=None):
    return PlayerUtility(
        player_id=player_id,
        utility=utility,
        eligible_positions=frozenset(positions),
        primary_position=primary,
    )


def slot(slot_id, positions):
    return RosterSlot(slot_id=slot_id, accepted_positions=frozenset(positions))


def test_authoritative_league_has_288_constrained_and_368_scoring_slots():
    active = build_league_active_slots()
    scoring = build_league_scoring_slots()

    assert len(active) == 16 * 18
    assert len(scoring) == 16 * 23
    assert sum("-GDEF-" in item.slot_id for item in active) == 16 * 4
    assert sum("-KDEF-" in item.slot_id for item in active) == 16 * 2
    assert sum("-MID-" in item.slot_id for item in active) == 16 * 5
    assert sum("-RUC-" in item.slot_id for item in active) == 16
    assert sum("-GFWD-" in item.slot_id for item in active) == 16 * 4
    assert sum("-KFWD-" in item.slot_id for item in active) == 16 * 2
    assert sum("-FREE-" in item.slot_id for item in scoring) == 16 * 5


def test_fast_solver_matches_reference_solver_on_small_problem():
    players = [
        player("dual", 92, {"MID", "GFWD"}, primary="MID"),
        player("mid", 90, {"MID"}),
        player("forward", 75, {"GFWD"}),
        player("replacement", 60, {"GFWD"}),
    ]
    slots = [slot("T01-MID-1", {"MID"}), slot("T01-GFWD-1", {"GFWD"})]

    fast = optimise_league_active_lineups(players, slots)
    reference = optimise_roster(players, slots)

    assert fast.total_utility == reference.total_utility == 182
    assert {(x.slot_id, x.player_id) for x in fast.assignments} == {
        (x.slot_id, x.player_id) for x in reference.assignments
    }


def test_league_marginal_value_reflects_replacement_not_raw_score():
    players = [
        player("forward_80", 80, {"GFWD"}),
        player("forward_65", 65, {"GFWD"}),
        player("mid_100", 100, {"MID"}),
        player("mid_95", 95, {"MID"}),
    ]
    slots = [slot("T01-GFWD-1", {"GFWD"}), slot("T01-MID-1", {"MID"})]

    assert marginal_league_utility(players, "forward_80", slots) == 15
    assert marginal_league_utility(players, "mid_100", slots) == 5


def test_forward_to_mid_flexibility_can_be_zero():
    players = [
        player("forward_dual", 80, {"GFWD", "MID"}, primary="GFWD"),
        player("forward_75", 75, {"GFWD"}),
        player("mid_100", 100, {"MID"}),
    ]
    slots = [slot("T01-GFWD-1", {"GFWD"}), slot("T01-MID-1", {"MID"})]

    assert league_flexibility_value(players, "forward_dual", slots) == 0


def test_mid_to_forward_flexibility_can_be_material():
    players = [
        player("mid_dual", 90, {"MID", "GFWD"}, primary="MID"),
        player("mid_89", 89, {"MID"}),
        player("forward_70", 70, {"GFWD"}),
    ]
    slots = [slot("T01-GFWD-1", {"GFWD"}), slot("T01-MID-1", {"MID"})]

    assert league_flexibility_value(players, "mid_dual", slots) == 19


def test_position_summary_reports_assignment_cut_lines():
    players = [
        player("mid_100", 100, {"MID"}),
        player("mid_90", 90, {"MID"}),
        player("forward_80", 80, {"GFWD"}),
    ]
    slots = [
        slot("T01-MID-1", {"MID"}),
        slot("T01-MID-2", {"MID"}),
        slot("T01-GFWD-1", {"GFWD"}),
    ]
    result = optimise_league_active_lineups(players, slots)

    assert assigned_position_summary(result) == {
        "GFWD": {"count": 1.0, "minimum": 80.0, "median": 80.0, "maximum": 80.0},
        "MID": {"count": 2.0, "minimum": 90.0, "median": 95.0, "maximum": 100.0},
    }


def test_infeasible_eligibility_fails_explicitly():
    players = [player("mid", 100, {"MID"}), player("mid2", 90, {"MID"})]
    slots = [slot("T01-MID-1", {"MID"}), slot("T01-GFWD-1", {"GFWD"})]

    try:
        optimise_league_active_lineups(players, slots)
    except ValueError as exc:
        assert "cannot all be filled" in str(exc)
    else:
        raise AssertionError("expected infeasible allocation to fail")
