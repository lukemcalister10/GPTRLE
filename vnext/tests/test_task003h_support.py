import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analyse_task003h_support import raw_feature_summary, transformed_summary


class Artifact:
    def __init__(self):
        self.preprocessor = ColumnTransformer(
            [
                (
                    "n",
                    Pipeline(
                        [("i", SimpleImputer(strategy="median")), ("s", StandardScaler())]
                    ),
                    ["pick", "tenure", "age", "total_games", "qualifying_seasons", "last_avg", "last_games", "prev_avg", "prev_games", "weighted_avg", "career_best", "recent_best", "avg_trend", "games_last_2", "seasons_observed"],
                ),
                (
                    "c",
                    Pipeline(
                        [("i", SimpleImputer(strategy="most_frequent")), ("o", OneHotEncoder(handle_unknown="ignore"))]
                    ),
                    ["position", "draft_type"],
                ),
            ]
        )


def frame(position=("MID", "RUC"), draft_type=("ND", "RD")):
    n = len(position)
    data = {
        "pick": np.arange(1, n + 1, dtype=float),
        "tenure": np.arange(n, dtype=float),
        "age": np.linspace(19, 25, n),
        "total_games": np.arange(n, dtype=float) * 10,
        "qualifying_seasons": np.zeros(n),
        "last_avg": np.linspace(0, 80, n),
        "last_games": np.linspace(0, 20, n),
        "prev_avg": np.linspace(0, 70, n),
        "prev_games": np.linspace(0, 18, n),
        "weighted_avg": np.linspace(0, 75, n),
        "career_best": np.linspace(0, 90, n),
        "recent_best": np.linspace(0, 85, n),
        "avg_trend": np.linspace(-5, 5, n),
        "games_last_2": np.linspace(0, 40, n),
        "seasons_observed": np.arange(1, n + 1, dtype=float),
        "position": list(position),
        "draft_type": list(draft_type),
    }
    return pd.DataFrame(data)


def test_raw_feature_summary_flags_numeric_extrapolation_and_unseen_categories():
    reference = frame()
    probe = frame(position=("FWD",), draft_type=("MSD",))
    probe.loc[0, "age"] = 31

    result = raw_feature_summary(reference, probe)

    age = result[result["feature"].eq("age")].iloc[0]
    position = result[result["feature"].eq("position")].iloc[0]
    assert age["probe_above_reference_max"] == 1
    assert position["unseen_categories"] == "FWD"
    assert position["probe_unseen_category_rows"] == 1


def test_transformed_summary_reports_probe_distance_and_norm_exceedance():
    reference = frame(position=("MID", "RUC", "DEF"), draft_type=("ND", "RD", "ND"))
    artifact = Artifact()
    artifact.preprocessor.fit(reference)
    probe = reference.iloc[[0]].copy()
    probe.loc[probe.index[0], "age"] = 99

    result = transformed_summary(artifact, reference, probe)

    assert result["n_reference"] == 3
    assert result["n_probe"] == 1
    assert result["nearest_train_distance_median"] > 0
    assert result["probe_norm_above_reference_p99_rows"] == 1
