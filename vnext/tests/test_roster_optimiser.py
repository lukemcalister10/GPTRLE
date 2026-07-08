from roster_optimiser import (
    PlayerUtility,
    RosterSlot,
    build_slots,
    flexibility_value,
    marginal_roster_utility,
    optimise_roster,
)


def player(player_id, utility, positions, primary=None):
    return PlayerUtility(
        player_id=player_id,
        utility=utility,
        eligible_positions=frozenset(positions),
        primary_position=primary,
    )


def slot(slot_id, positions, multiplier=1.0):
    return RosterSlot(
        slot_id=slot_id,
        accepted_positions=frozenset(positions),
        utility_multiplier=multiplier,
    )


def test_scarce_forward_can_have_more_marginal_value_than_higher_scoring_midfielder():
    players = [
        player("forward_80", 80, {"FWD"}),
        player("replacement_forward_65", 65, {"FWD"}),
        player("mid_100", 100, {"MID"}),
        player("mid_95", 95, {"MID"}),
    ]
    slots = [slot("FWD-1", {"FWD"}), slot("MID-1", {"MID"})]

    assert marginal_roster_utility(players, slots, "forward_80") == 15
    assert marginal_roster_utility(players, slots, "mid_100") == 5


def test_forward_adding_midfield_eligibility_can_be_worth_zero():
    players = [
        player("forward_dual", 80, {"FWD", "MID"}, primary="FWD"),
        player("forward_75", 75, {"FWD"}),
        player("mid_100", 100, {"MID"}),
    ]
    slots = [slot("FWD-1", {"FWD"}), slot("MID-1", {"MID"})]

    assert flexibility_value(players, slots, "forward_dual") == 0


def test_midfielder_adding_forward_eligibility_can_unlock_material_value():
    players = [
        player("mid_dual", 90, {"MID", "FWD"}, primary="MID"),
        player("mid_89", 89, {"MID"}),
        player("forward_70", 70, {"FWD"}),
    ]
    slots = [slot("FWD-1", {"FWD"}), slot("MID-1", {"MID"})]

    assert flexibility_value(players, slots, "mid_dual") == 19


def test_removal_reoptimises_other_players_across_positions():
    players = [
        player("dual_90", 90, {"MID", "FWD"}),
        player("mid_88", 88, {"MID"}),
        player("forward_80", 80, {"FWD"}),
        player("replacement_forward_65", 65, {"FWD"}),
    ]
    slots = [slot("FWD-1", {"FWD"}), slot("MID-1", {"MID"})]

    result = optimise_roster(players, slots)
    assert result.total_utility == 178
    assert {(x.slot_id, x.player_id) for x in result.assignments} == {
        ("FWD-1", "dual_90"),
        ("MID-1", "mid_88"),
    }
    assert marginal_roster_utility(players, slots, "dual_90") == 10


def test_bench_multiplier_counts_only_declared_coverage_utility():
    players = [
        player("starter", 100, {"MID"}),
        player("bench", 90, {"MID"}),
    ]
    slots = [
        slot("MID-1", {"MID"}),
        slot("BENCH-1", {"MID"}, multiplier=0.2),
    ]

    result = optimise_roster(players, slots)
    assert result.total_utility == 118
    assert {(x.slot_id, x.player_id, x.utility) for x in result.assignments} == {
        ("BENCH-1", "bench", 18),
        ("MID-1", "starter", 100),
    }


def test_build_slots_is_deterministic_and_validates_configuration():
    slots = build_slots(
        {"MID": 2, "FWD": 1},
        {"MID": {"MID"}, "FWD": {"FWD"}},
        multipliers={"MID": 0.9},
    )

    assert [slot.slot_id for slot in slots] == ["FWD-1", "MID-1", "MID-2"]
    assert [slot.utility_multiplier for slot in slots] == [1.0, 0.9, 0.9]


def test_infeasible_roster_fails_instead_of_silently_dropping_slot():
    players = [player("mid", 100, {"MID"}), player("mid_2", 90, {"MID"})]
    slots = [slot("MID-1", {"MID"}), slot("FWD-1", {"FWD"})]

    try:
        optimise_roster(players, slots)
    except ValueError as exc:
        assert "cannot all be filled" in str(exc)
    else:
        raise AssertionError("expected infeasible roster to fail")
