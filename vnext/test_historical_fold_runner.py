from pathlib import Path
import pandas as pd
import pytest

from benchmark import LOCKED_FOLDS, PREDICTION_KEY, QUANTILE_COLUMNS, normalise_predictions, REQUIRED_PREDICTION_COLUMNS
from run_historical_folds import add_residual_quantiles, train_artifacts, MODEL_ID


def tiny_dataset():
    rows=[]
    for origin in range(2008, 2018):
        for i in range(18):
            r={"key":f"p{i}","player":f"P{i}","origin_year":origin,"position":"MID","draft_type":"ND","pick":i+1,"tenure":origin-2007,"age":20+i%5,"total_games":20+i,"qualifying_seasons":1,"last_avg":60+i,"last_games":10,"prev_avg":55+i,"prev_games":8,"weighted_avg":58+i,"career_best":70+i,"recent_best":65+i,"avg_trend":1.0,"games_last_2":18,"seasons_observed":2}
            for lead in range(1,6):
                games=0 if i % 7 == 0 else 8+(i+lead)%10; avg=55+i+lead
                meaningful=int(games>=6)
                r[f"l{lead}_games"]=games; r[f"l{lead}_avg"]=avg if meaningful else 0.0; r[f"l{lead}_points"]=games*avg; r[f"l{lead}_meaningful"]=meaningful
                for t in (80,90,100,110,120): r[f"l{lead}_{t}"]=int(avg>=t)
            rows.append(r)
    return pd.DataFrame(rows)


def base_pred(n=2):
    return pd.DataFrame({"p_meaningful":[0.7]*n,"cond_games":[12.0]*n,"cond_avg":[80.0]*n,"exp_games":[8.4]*n,"exp_avg":[56.0]*n,"exp_points":[672.0]*n,"p80":[0.4]*n,"p90":[0.3]*n,"p100":[0.2]*n,"p110":[0.1]*n,"p120":[0.05]*n})


def test_every_locked_origin_and_lead_present():
    assert {(lead, origin) for lead, origins in LOCKED_FOLDS.items() for origin in origins}
    assert sum(len(v) for v in LOCKED_FOLDS.values()) == 25


def test_strict_historical_training_cutoff(tmp_path: Path):
    artifacts, manifest, counts = train_artifacts(tiny_dataset(), tmp_path)
    for _, row in counts.iterrows():
        assert row.train_max_origin + row.lead < row.origin_year
        assert row.training_target_max_year < row.origin_year
    assert set(artifacts) == {(lead, origin) for lead, origins in LOCKED_FOLDS.items() for origin in origins}


def test_no_current_or_future_fields_needed_for_prediction_quantiles():
    class A: games_resid_sd=2.0; avg_resid_sd=5.0
    rows=pd.DataFrame({"player_key":["a","b"],"origin_year":[2018,2018],"lead":[1,1],"current_club":["X","Y"],"future_position":["RUC","MID"]})
    a=add_residual_quantiles(base_pred(2), A(), rows)
    b=add_residual_quantiles(base_pred(2), A(), rows.drop(columns=["current_club","future_position"]))
    pd.testing.assert_frame_equal(a, b)


def test_quantiles_non_crossing_and_deterministic():
    class A: games_resid_sd=3.0; avg_resid_sd=12.0
    rows=pd.DataFrame({"player_key":["a"],"origin_year":[2018],"lead":[1]})
    first=add_residual_quantiles(base_pred(1), A(), rows)
    second=add_residual_quantiles(base_pred(1), A(), rows)
    pd.testing.assert_frame_equal(first, second)
    assert (first[list(QUANTILE_COLUMNS)].diff(axis=1).iloc[:,1:] >= -1e-12).all().all()
    assert first[list(QUANTILE_COLUMNS)].nunique(axis=1).iloc[0] > 1


def test_schema_validation_and_malformed_output_failures():
    row={"player_key":"p1","origin_year":2018,"lead":1,"p_meaningful":0.5,"cond_games":10,"cond_avg":80,"exp_games":5,"exp_points":400,"p_avg_ge_80":0.4,"p_avg_ge_90":0.3,"p_avg_ge_100":0.2,"p_avg_ge_110":0.1,"p_avg_ge_120":0.05}
    for c in QUANTILE_COLUMNS: row[c]=400.0
    ok=normalise_predictions(MODEL_ID, pd.DataFrame([row]))
    assert list(ok.columns)==["model_id", *REQUIRED_PREDICTION_COLUMNS]
    bad=pd.DataFrame([row]).drop(columns=[QUANTILE_COLUMNS[-1]])
    with pytest.raises(ValueError, match="missing columns"):
        normalise_predictions(MODEL_ID, bad)


def test_exact_locked_key_coverage_fixture():
    targets=pd.DataFrame({"player_key":["a","b"],"origin_year":[2018,2018],"lead":[1,1]})
    preds=targets.copy()
    for c in [c for c in REQUIRED_PREDICTION_COLUMNS if c not in PREDICTION_KEY]: preds[c]=0.1 if c.startswith('p_') else 1.0
    preds['p_avg_ge_90']=0.09; preds['p_avg_ge_100']=0.08; preds['p_avg_ge_110']=0.07; preds['p_avg_ge_120']=0.06
    norm=normalise_predictions(MODEL_ID, preds)
    assert norm[PREDICTION_KEY].equals(targets[PREDICTION_KEY])
