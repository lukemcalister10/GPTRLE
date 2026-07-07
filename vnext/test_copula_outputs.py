from pathlib import Path
import pandas as pd

def test_copula_outputs():
    root=Path('output_stage4/copula')
    s=pd.read_csv(root/'copula_vs_independence.csv')
    assert set(s.threshold)=={90,100,110}
    assert s.selected_rho.between(0,0.95).all()
    assert s[['independence_brier','copula_brier']].notna().all().all()
    p=pd.read_csv(root/'observed_persistence.csv')
    assert (p.mean_pairwise_event_corr>0).all()
