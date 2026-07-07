from pathlib import Path
import pandas as pd
BASE=Path(__file__).parent/'output'/'eval_v3_fast'
def test_prediction_rows_are_complete():
    d=pd.read_csv(BASE/'predictions.csv')
    required=['key','origin_year','lead','p_meaningful','cond_games','cond_avg','exp_points']
    assert not d[required].isna().any().any()
def test_probabilities_are_bounded_and_nested():
    d=pd.read_csv(BASE/'predictions.csv')
    cols=['p_meaningful','p80','p90','p100','p110','p120']
    assert ((d[cols]>=0)&(d[cols]<=1)).all().all()
    assert (d.p80>=d.p90).all() and (d.p90>=d.p100).all() and (d.p100>=d.p110).all() and (d.p110>=d.p120).all()
def test_all_five_leads_present():
    d=pd.read_csv(BASE/'predictions.csv')
    assert sorted(d.lead.unique().tolist())==[1,2,3,4,5]
