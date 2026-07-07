import numpy as np
import pandas as pd

from model_artifacts_event_logistic import make_event_classifier, replace_event_layer


class Preprocessor:
    def transform(self, rows):
        return rows[["x1", "x2"]].to_numpy(float)


class Artifact:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.event_model = "old-event"
        self.event_calibrator = "old-calibrator"
        self.games_model = "games"
        self.avg_model = "average"
        self.threshold_models = {80: "threshold"}
        self.threshold_calibrators = {80: "threshold-calibrator"}
        self.games_resid_sd = 3.25
        self.avg_resid_sd = 11.5


def rows():
    x = np.linspace(-2.0, 2.0, 40)
    return pd.DataFrame(
        {"x1": x, "x2": np.sin(x), "l1_meaningful": (x > 0).astype(int)}
    )


def test_candidate_spec_is_fixed():
    model = make_event_classifier()
    assert model.C == 0.35
    assert model.max_iter == 500
    assert model.solver == "lbfgs"
    assert model.penalty == "l2"
    assert model.tol == 1e-4


def test_only_event_layer_is_replaced():
    artifact = Artifact()
    before = (
        artifact.games_model,
        artifact.avg_model,
        artifact.threshold_models,
        artifact.threshold_calibrators,
        artifact.games_resid_sd,
        artifact.avg_resid_sd,
    )
    data = rows()
    replace_event_layer(artifact, data.iloc[:30], data.iloc[30:], 1)
    after = (
        artifact.games_model,
        artifact.avg_model,
        artifact.threshold_models,
        artifact.threshold_calibrators,
        artifact.games_resid_sd,
        artifact.avg_resid_sd,
    )
    assert before == after
    assert artifact.event_model_family == "LogisticRegression"
    assert artifact.task003k_single_change == "meaningful_season_event_classifier"


def test_candidate_is_deterministic():
    data = rows()
    first = Artifact()
    second = Artifact()
    replace_event_layer(first, data.iloc[:30], data.iloc[30:], 1)
    replace_event_layer(second, data.iloc[:30], data.iloc[30:], 1)
    probe = data.iloc[5:15]
    x = first.preprocessor.transform(probe)
    np.testing.assert_array_equal(
        first.event_model.predict_proba(x),
        second.event_model.predict_proba(x),
    )
