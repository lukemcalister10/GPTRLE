import pytest

from scarcity_premium import ScarcityPolicy, scarcity_premium


CUTS = {
    "GDEF": 330.0,
    "KDEF": 250.0,
    "MID": 360.0,
    "RUC": 300.0,
    "GFWD": 335.0,
    "KFWD": 365.0,
}


def test_position_above_unrestricted_cut_line_receives_premium():
    result = scarcity_premium(
        intrinsic_value=365.0,
        eligible_positions=frozenset({"KFWD"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
    )

    assert result.scarcity_premium == pytest.approx(27.5)
    assert result.combined_value == pytest.approx(392.5)
    assert result.best_position == "KFWD"


def test_position_below_unrestricted_cut_line_receives_no_premium():
    result = scarcity_premium(
        intrinsic_value=400.0,
        eligible_positions=frozenset({"KDEF"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
    )

    assert result.scarcity_premium == 0
    assert result.combined_value == 400
    assert result.best_position is None


def test_players_below_cut_line_receive_smooth_nonzero_premium():
    near = scarcity_premium(
        intrinsic_value=340.0,
        eligible_positions=frozenset({"KFWD"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
    )
    far = scarcity_premium(
        intrinsic_value=200.0,
        eligible_positions=frozenset({"KFWD"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
    )

    assert near.scarcity_premium > far.scarcity_premium > 0


def test_dual_position_uses_best_premium_not_sum():
    dual = scarcity_premium(
        intrinsic_value=360.0,
        eligible_positions=frozenset({"MID", "KFWD"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
    )
    mid_only = scarcity_premium(
        intrinsic_value=360.0,
        eligible_positions=frozenset({"MID"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
    )
    kfwd_only = scarcity_premium(
        intrinsic_value=360.0,
        eligible_positions=frozenset({"KFWD"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
    )

    assert dual.scarcity_premium == max(mid_only.scarcity_premium, kfwd_only.scarcity_premium)
    assert dual.scarcity_premium < mid_only.scarcity_premium + kfwd_only.scarcity_premium


def test_owner_or_team_is_not_an_input():
    first = scarcity_premium(
        intrinsic_value=350.0,
        eligible_positions=frozenset({"GFWD"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
    )
    second = scarcity_premium(
        intrinsic_value=350.0,
        eligible_positions=frozenset({"GFWD"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
    )

    assert first == second


def test_policy_scale_and_bandwidth_are_explicit():
    base = scarcity_premium(
        intrinsic_value=365.0,
        eligible_positions=frozenset({"KFWD"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
    )
    scaled = scarcity_premium(
        intrinsic_value=365.0,
        eligible_positions=frozenset({"KFWD"}),
        position_cut_lines=CUTS,
        unrestricted_cut_line=310.0,
        policy=ScarcityPolicy(bandwidth=40.0, premium_scale=0.5),
    )

    assert scaled.scarcity_premium == pytest.approx(base.scarcity_premium * 0.5)


def test_invalid_inputs_fail():
    with pytest.raises(ValueError, match="non-empty"):
        scarcity_premium(
            intrinsic_value=300,
            eligible_positions=frozenset(),
            position_cut_lines=CUTS,
            unrestricted_cut_line=310,
        )

    with pytest.raises(KeyError, match="missing"):
        scarcity_premium(
            intrinsic_value=300,
            eligible_positions=frozenset({"UNKNOWN"}),
            position_cut_lines=CUTS,
            unrestricted_cut_line=310,
        )
