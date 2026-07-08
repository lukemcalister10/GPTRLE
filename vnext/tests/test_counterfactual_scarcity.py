import pytest

from counterfactual_scarcity import first_slot_scarcity_cost, relaxation_curve
from roster_optimiser import PlayerUtility, RosterSlot


def player(player_id, utility, positions):
    return PlayerUtility(player_id, utility, frozenset(positions))


def slot(slot_id, positions):
    return RosterSlot(slot_id, frozenset(positions))


def test_relaxing_nonbinding_constraint_has_zero_cost():
    players = [
        player("mid_100", 100, {"MID"}),
        player("mid_90", 90, {"MID"}),
        player("forward_80", 80, {"GFWD"}),
    ]
    slots = [slot("MID-1", {"MID"}), slot("FREE-1", {"MID", "GFWD"})]

    assert first_slot_scarcity_cost(players, slots, position="MID") == 0


def test_relaxing_binding_constraint_measures_lost_league_utility():
    players = [
        player("mid_100", 100, {"MID"}),
        player("mid_90", 90, {"MID"}),
        player("forward_50", 50, {"GFWD"}),
    ]
    slots = [slot("GFWD-1", {"GFWD"}), slot("FREE-1", {"MID", "GFWD"})]

    assert first_slot_scarcity_cost(players, slots, position="GFWD") == 40


def test_curve_reports_cumulative_and_marginal_costs():
    players = [
        player("mid_100", 100, {"MID"}),
        player("mid_90", 90, {"MID"}),
        player("forward_60", 60, {"GFWD"}),
        player("forward_50", 50, {"GFWD"}),
    ]
    slots = [
        slot("GFWD-1", {"GFWD"}),
        slot("GFWD-2", {"GFWD"}),
        slot("FREE-1", {"MID", "GFWD"}),
    ]

    curve = relaxation_curve(players, slots, position="GFWD", max_relaxations=2)

    assert curve[0].cumulative_cost == 30
    assert curve[0].marginal_cost == 30
    assert curve[1].cumulative_cost == 40
    assert curve[1].marginal_cost == 10


def test_equivalent_assignment_labels_do_not_change_cost():
    players = [
        player("dual_a", 100, {"MID", "GFWD"}),
        player("dual_b", 100, {"MID", "GFWD"}),
        player("forward", 70, {"GFWD"}),
    ]
    slots_a = [slot("GFWD-1", {"GFWD"}), slot("FREE-1", {"MID", "GFWD"})]
    slots_b = [slot("FREE-1", {"MID", "GFWD"}), slot("GFWD-1", {"GFWD"})]

    assert first_slot_scarcity_cost(players, slots_a, position="GFWD") == first_slot_scarcity_cost(
        players, slots_b, position="GFWD"
    )


def test_invalid_relaxation_fails():
    players = [player("mid", 100, {"MID"})]
    slots = [slot("MID-1", {"MID"})]

    with pytest.raises(ValueError, match="cannot relax"):
        relaxation_curve(players, slots, position="MID", max_relaxations=2)
    with pytest.raises(ValueError, match="unknown"):
        first_slot_scarcity_cost(players, slots, position="UNKNOWN")
