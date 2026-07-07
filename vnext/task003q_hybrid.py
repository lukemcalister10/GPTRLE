from __future__ import annotations

import numpy as np
import pandas as pd

KEY = ["player_key", "origin_year", "lead"]
COLUMNS = ["p_meaningful", "exp_games", "exp_points"]


def blend_weight(age, lead):
    age = np.asarray(age, dtype=float)
    lead = np.asarray(lead, dtype=int)
    short = np.where(age <= 28, 1.0, np.where(age < 32, (32.0 - age) / 4.0, 0.0))
    long = np.where(age <= 26, 1.0, np.where(age < 28, (28.0 - age) / 2.0, 0.0))
    return np.clip(np.where(lead == 5, long, short), 0.0, 1.0)


def blend_predictions(current: pd.DataFrame, candidate: pd.DataFrame, snapshots: pd.DataFrame) -> pd.DataFrame:
    ages = snapshots[["player_key", "origin_year", "age"]].drop_duplicates()
    joined = current.merge(ages, on=["player_key", "origin_year"], validate="many_to_one")
    joined = joined.merge(candidate[KEY + COLUMNS], on=KEY, validate="one_to_one", suffixes=("_current", "_candidate"))
    weight = blend_weight(joined["age"], joined["lead"])
    output = current.copy()
    for column in COLUMNS:
        output[column] = joined[column + "_current"] + weight * (joined[column + "_candidate"] - joined[column + "_current"])
    output["model_id"] = "vnext_task003q_hybrid"
    output["task003q_weight"] = weight
    return output
