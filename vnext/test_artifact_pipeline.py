from pathlib import Path
import json, joblib, pandas as pd
BASE=Path(__file__).parent/'output'
def test_all_artifacts_exist():
    for l in range(1,6): assert (BASE/'artifacts'/f'lead_{l}.joblib').exists()
def test_artifact_manifest_complete():
    m=json.loads((BASE/'artifacts'/'manifest.json').read_text()); assert sorted(map(int,m['leads']))==[1,2,3,4,5]
def test_current_board_complete_and_bounded():
    d=pd.read_csv(BASE/'current'/'current_five_year_simulated_utility.csv')
    assert len(d)>700 and d.key.nunique()==len(d)
    ps=[c for c in d if c.startswith('p_')]
    assert ((d[ps]>=0)&(d[ps]<=1)).all().all()
    assert (d.five_year_utility_p10<=d.five_year_utility_median).all()
    assert (d.five_year_utility_median<=d.five_year_utility_p90).all()
def test_no_training_during_inference_contract():
    m=json.loads((BASE/'current'/'simulation_manifest.json').read_text()); assert m['players']>700
