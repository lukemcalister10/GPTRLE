import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import numpy as np
import pytest

from task049_three_state_point_distribution import (
    QCOLS,
    generate_three_state_predictions,
    estimate_short_season_evidence,
)
from analyse_task048_ridge_uncertainty import bootstrap_ci


def dataset(short=True):
    rows=[]
    for oy in range(2008, 2014):
        rows.append({'key':f'z{oy}','origin_year':oy,'l1_games':0,'l1_points':0})
        if short:
            rows.append({'key':f's{oy}','origin_year':oy,'l1_games':(oy%5)+1,'l1_points':((oy%5)+1)*50})
        rows.append({'key':f'm{oy}','origin_year':oy,'l1_games':10,'l1_points':800})
    return pd.DataFrame(rows)


def predictions():
    return pd.DataFrame({
        'player_key':['a','b'], 'origin_year':[2018,2018], 'lead':[1,1],
        'p_meaningful':[0.4,0.8], 'cond_games':[12.0,18.0], 'cond_avg':[70.0,95.0],
        'exp_games':[4.8,14.4], 'exp_points':[336.0,1368.0],
        **{c:[0.0,0.0] for c in QCOLS},
        'p_avg_ge_80':[0.1,0.2]
    })


def fold_manifest():
    return pd.DataFrame({'lead':[1], 'origin_year':[2018], 'games_resid_sd':[1.0], 'avg_resid_sd':[5.0]})


def test_state_probabilities_sum_and_support_constraints_and_positive_short_points():
    ev=estimate_short_season_evidence(dataset(),1,2018)
    assert ev.p_zero_given_nonmeaningful + ev.p_short_given_nonmeaningful == pytest.approx(1)
    assert set(ev.short_games) <= {1,2,3,4,5}
    assert all(r > 0 for r in ev.short_rates)
    out, evidence, recon = generate_three_state_predictions(predictions(), dataset(), fold_manifest(), sample_count=4096)
    assert np.allclose(recon[['p_zero_state','p_short_state','p_meaningful_state']].sum(axis=1), 1.0)
    assert (recon.p_short_state > 0).all()
    assert set(evidence.short_games.iloc[0].split('|')) <= {'1','2','3','4','5'}
    assert ((out[QCOLS] >= 0).all()).all()
    assert (np.diff(out[QCOLS].to_numpy(float), axis=1) >= -1e-12).all()


def test_exact_point_forecast_preservation_and_determinism_and_unchanged_outputs():
    base=predictions()
    out1, _, recon1 = generate_three_state_predictions(base, dataset(), fold_manifest(), sample_count=4096)
    out2, _, recon2 = generate_three_state_predictions(base, dataset(), fold_manifest(), sample_count=4096)
    pd.testing.assert_frame_equal(out1, out2)
    assert (recon1.abs_delta <= 1e-8).all()
    pd.testing.assert_series_equal(out1.exp_points, base.exp_points)
    for col in ['p_meaningful','cond_games','cond_avg','exp_games','p_avg_ge_80']:
        pd.testing.assert_series_equal(out1[col], base[col])


def test_meaningful_branch_constraints_from_generated_quantiles_are_nonnegative():
    out, _, _ = generate_three_state_predictions(predictions(), dataset(), fold_manifest(), sample_count=4096)
    assert ((out[QCOLS] >= 0).all()).all()
    # Generator clips meaningful games to 6-23 internally; non-crossing positive high quantiles prove usable support.
    assert (out.points_q97 > 0).all()


def test_unequal_row_count_pooled_cluster_bootstrap_runs():
    wide=pd.DataFrame({'player_key':['a','a','b'], 'points':[1.,2.,3.]})
    for c in QCOLS:
        wide[f'{c}_task047']=[1.,1.,4.]
        wide[f'{c}_task012']=[0.,2.,3.]
    boot=bootstrap_ci(wide, reps=10, seed=1)
    assert set(boot.metric) == {'primary_mean_pinball', *QCOLS}
    assert (boot.replications == 10).all()


def test_fail_loud_missing_short_support():
    with pytest.raises(ValueError, match='missing short-season training support'):
        estimate_short_season_evidence(dataset(short=False),1,2018)


def test_generated_branch_fails_on_missing_manifest_residual_scales():
    with pytest.raises(ValueError, match='missing residual-scale columns'):
        generate_three_state_predictions(
            predictions(),
            dataset(),
            pd.DataFrame({'lead': [1], 'origin_year': [2018], 'games_resid_sd': [1.0]}),
            sample_count=256,
        )


def test_generated_branch_fails_on_duplicate_manifest_rows():
    dup = pd.concat([fold_manifest(), fold_manifest()], ignore_index=True)
    with pytest.raises(ValueError, match='expected exactly one fold manifest row'):
        generate_three_state_predictions(predictions(), dataset(), dup, sample_count=256)


def test_generated_branch_outputs_state_reconciliation_schema():
    out, evidence, recon = generate_three_state_predictions(predictions(), dataset(), fold_manifest(), sample_count=4096)
    assert list(out[QCOLS].columns) == QCOLS
    assert {'p_zero_state', 'p_short_state', 'p_meaningful_state', 'abs_delta'} <= set(recon.columns)
    assert {'n_zero', 'n_short', 'n_meaningful', 'short_rates_count'} <= set(evidence.columns)
    assert (evidence.n_short > 0).all()
    assert (recon.abs_delta <= 1e-8).all()
