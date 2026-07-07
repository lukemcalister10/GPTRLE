import numpy as np

from model_artifacts_conditional_calibrated import (
    ClippedIdentityCalibrator,
    calibrate_conditional_predictions,
    fit_conditional_calibrator,
)


def test_isotonic_conditional_calibrator_is_monotonic_and_bounded():
    raw = np.linspace(1.0, 10.0, 40)
    actual = np.linspace(6.0, 20.0, 40)
    calibrator, metadata = fit_conditional_calibrator(
        raw,
        actual,
        lower=6.0,
        upper=23.0,
    )
    values = calibrator.predict(np.array([-10.0, 2.0, 5.0, 20.0]))
    assert metadata["method"] == "isotonic_temporal_mean_calibration"
    assert np.all(np.diff(values) >= 0.0)
    assert values.min() >= 6.0
    assert values.max() <= 23.0


def test_small_calibration_sample_falls_back_explicitly():
    calibrator, metadata = fit_conditional_calibrator(
        [1.0, 2.0],
        [6.0, 8.0],
        lower=6.0,
        upper=23.0,
    )
    assert isinstance(calibrator, ClippedIdentityCalibrator)
    assert metadata["fallback_reason"] == "insufficient_rows"
    assert calibrator.predict([-1.0, 30.0]).tolist() == [6.0, 23.0]


def test_calibrated_components_are_applied_independently():
    class Artifact:
        games_calibrator = ClippedIdentityCalibrator(6.0, 23.0)
        avg_calibrator = ClippedIdentityCalibrator(20.0, 145.0)

    games, average = calibrate_conditional_predictions(
        Artifact(),
        raw_games=[2.0, 30.0],
        raw_avg=[10.0, 200.0],
    )
    assert games.tolist() == [6.0, 23.0]
    assert average.tolist() == [20.0, 145.0]
