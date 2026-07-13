import numpy as np
import pandas as pd
import pytest

from task049_three_state_distribution import (
    QCOLS, SAMPLE_COUNT, build_short_support, candidate_minus_baseline_bootstrap,
    compare_unchanged_outputs, generate_three_state_predictions, seed_for, validate_fold_manifest,
)


def training():
    return pd.DataFrame({"origin_year":[2008,2008,2009,2009,2010,2010],"lead":[1]*6,"games":[0,1,3,5,8,12],"points":[0,50,180,300,700,1000]})


def manifest():
    return pd.DataFrame({"origin_year":[2012],"lead":[1],"games_resid_sd":[2.0],"avg_resid_sd":[5.0]})


def preds():
    return pd.DataFrame({"player_key":["a","b"],"origin_year":[2012,2012],"lead":[1,1],"p_meaningful":[.6,.2],"cond_games":[12,10],"cond_avg":[80,70],"exp_games":[8,3],"exp_points":[600.0,180.0],"points_q10":[0,0],"points_q25":[0,0],"points_q50":[100,0],"points_q75":[700,100],"points_q90":[900,300],"points_q97":[1100,500]})


def test_branch_diagnostics_and_invariants():
    sup=build_short_support(training(), manifest())
    cand, diag=generate_three_state_predictions(preds(), sup)
    assert np.allclose(diag[["p_zero","p_short","p_meaningful"]].sum(axis=1), 1.0)
    nonnull=diag.short_draw_count.gt(0)
    assert diag.loc[nonnull,"short_games_min"].between(1,5).all()
    assert diag.loc[nonnull,"short_games_max"].between(1,5).all()
    assert diag.loc[nonnull,"adjusted_short_points_min"].gt(0).all()
    assert diag.loc[diag.meaningful_draw_count.gt(0),"meaningful_games_min"].between(6,23).all()
    assert diag.loc[diag.meaningful_draw_count.gt(0),"meaningful_games_max"].between(6,23).all()
    cand2, diag2=generate_three_state_predictions(preds(), sup)
    pd.testing.assert_frame_equal(cand[QCOLS], cand2[QCOLS])
    pd.testing.assert_frame_equal(diag, diag2)
    assert (cand[QCOLS].to_numpy() >= 0).all()
    assert (np.diff(cand[QCOLS].to_numpy(), axis=1) >= -1e-12).all()
    assert np.allclose(diag.draw_mean_after, preds().exp_points, atol=1e-8)
    assert diag.moment_error_after.abs().max() <= 1e-8


def test_locked_generator_contract():
    assert SAMPLE_COUNT == 2048
    expected = 709084106
    assert seed_for("player-a", 2020, 3) == expected


def test_schema_and_non_quantile_unchanged():
    p=preds(); cand=p.copy(); cand["points_q50"] += 1
    comp=compare_unchanged_outputs(p, cand)
    assert set(comp.column) == set(p.columns) - set(QCOLS)
    bad=cand.copy(); bad["exp_points"] += .01
    with pytest.raises(ValueError, match="non-quantile"):
        compare_unchanged_outputs(p, bad)
    with pytest.raises(ValueError, match="schemas differ"):
        compare_unchanged_outputs(p, cand.drop(columns=["exp_games"]))


def test_residual_scale_fail_loud():
    for m in [manifest().drop(columns=["avg_resid_sd"]), pd.concat([manifest(), manifest()]), manifest().assign(games_resid_sd=[0.0]), manifest().assign(avg_resid_sd=[np.inf])]:
        with pytest.raises(ValueError):
            validate_fold_manifest(m)


def test_missing_short_support_fails():
    with pytest.raises(ValueError, match="missing short-season support"):
        build_short_support(training().query("games != 3 and games != 5 and games != 1"), manifest())


def test_pooled_bootstrap_unequal_player_rows_hand_computed():
    wide=pd.DataFrame({"player_key":["a","a","b"],"points":[10.,20.,30.],"points_q10_baseline":[0.,0.,0.],"points_q10_candidate":[1.,2.,3.]})
    for c in QCOLS[1:]:
        wide[f"{c}_baseline"]=wide.points; wide[f"{c}_candidate"]=wide.points
    ci, inv=candidate_minus_baseline_bootstrap(wide, reps=10, seed=49049)
    expected=np.mean([-.1,-.2,-.3])
    assert ci.loc[ci.metric.eq("points_q10"),"observed_diff_candidate_minus_baseline"].iloc[0] == pytest.approx(expected)
    assert (inv.abs_delta <= 1e-12).all()
