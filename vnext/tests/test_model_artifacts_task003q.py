import pandas as pd
import model_artifacts_task003q as hybrid

class DummyArtifact:
    train_max_origin=2020
    n_fit=1
    n_cal=1

def test_train_and_predict_hybrid(monkeypatch):
    monkeypatch.setattr(hybrid.model_artifacts,"train_lead",lambda train,lead:DummyArtifact())
    monkeypatch.setattr(hybrid.model_artifacts_event_logistic,"train_lead",lambda train,lead:DummyArtifact())
    artifact=hybrid.train_lead(pd.DataFrame({"x":[1]}),1)
    current=pd.DataFrame({"p_meaningful":[0.2],"exp_games":[2.0],"exp_points":[100.0],"exp_avg":[50.0]})
    candidate=pd.DataFrame({"p_meaningful":[0.6],"exp_games":[6.0],"exp_points":[300.0],"exp_avg":[50.0]})
    monkeypatch.setattr(hybrid.model_artifacts,"predict",lambda artifact,rows:current.copy())
    monkeypatch.setattr(hybrid.model_artifacts_event_logistic,"predict",lambda artifact,rows:candidate.copy())
    rows=pd.DataFrame({"player_key":["p"],"origin_year":[2020],"age":[30.0]})
    result=hybrid.predict(artifact,rows)
    assert result.loc[0,"task003q_weight"]==0.5
    assert result.loc[0,"p_meaningful"]==0.4
    assert result.loc[0,"exp_games"]==4.0
    assert result.loc[0,"exp_points"]==200.0
    assert result.loc[0,"exp_avg"]==50.0
