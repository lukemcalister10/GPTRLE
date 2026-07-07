import pandas as pd
from evaluate_v2_linear import tc

def test_target_column_mapping():
    assert tc(1,'games')=='next_games'
    assert tc(3,'games')=='h3_games'
    assert tc(5,'best_avg')=='h5_best_avg'

def test_training_cutoff_finishes_before_test_origin():
    for h,start in [(1,2023),(3,2021),(5,2019)]:
        origins=pd.Series(range(2008,start))
        legal=origins[origins+h<start]
        assert (legal+h<start).all()
        assert legal.max()+h==start-1
