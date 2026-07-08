import pytest

from player_comparison_export import (
    ForecastValueRow,
    build_export_rows,
    build_player_comparisons,
)

YEARS = (2027, 2028, 2029, 2030, 2031)


def rows_for(player_id, values, *, name=None, positions=None, owner=None, uncertainty=0):
    return [
        ForecastValueRow(
            player_id=player_id,
            forecast_year=year,
            expected_utility=value,
            uncertainty=uncertainty,
            player_name=name,
            positions=positions,
            current_owner=owner,
        )
        for year, value in zip(YEARS, values, strict=True)
    ]


def test_builds_three_values_from_one_forecast_vector():
    comparisons = build_player_comparisons(
        rows_for("veteran", [100, 90, 80, 70, 60])
        + rows_for("prospect", [60, 70, 80, 90, 100]),
        forecast_years=YEARS,
    )
    by_id = {row.player_id: row for row in comparisons}

    assert by_id["veteran"].contender_value > by_id["prospect"].contender_value
    assert by_id["prospect"].rebuilder_value > by_id["veteran"].rebuilder_value


def test_export_contains_deterministic_ranks_and_metadata():
    output = build_export_rows(
        rows_for("a", [100] * 5, name="Player A", positions="MID", owner="Adelaide")
        + rows_for("b", [80] * 5, name="Player B", positions="GFWD", owner="Free Agents"),
        forecast_years=YEARS,
    )

    assert output[0]["player_id"] == "a"
    assert output[0]["balanced_rank"] == 1
    assert output[0]["player_name"] == "Player A"
    assert output[0]["current_owner"] == "Adelaide"
    assert output[1]["balanced_rank"] == 2


def test_owner_metadata_does_not_change_value_or_rank():
    first = build_export_rows(
        rows_for("a", [100] * 5, owner="Adelaide")
        + rows_for("b", [90] * 5, owner="Brisbane"),
        forecast_years=YEARS,
    )
    second = build_export_rows(
        rows_for("a", [100] * 5, owner="Free Agents")
        + rows_for("b", [90] * 5, owner="Adelaide"),
        forecast_years=YEARS,
    )

    assert [(row["player_id"], row["balanced_value"], row["balanced_rank"]) for row in first] == [
        (row["player_id"], row["balanced_value"], row["balanced_rank"]) for row in second
    ]


def test_incomplete_or_duplicate_horizon_fails():
    incomplete = rows_for("a", [100] * 5)[:-1]
    with pytest.raises(ValueError, match="incomplete"):
        build_player_comparisons(incomplete, forecast_years=YEARS)

    duplicate = rows_for("a", [100] * 5)
    duplicate.append(duplicate[0])
    with pytest.raises(ValueError, match="duplicate"):
        build_player_comparisons(duplicate, forecast_years=YEARS)


def test_conflicting_metadata_fails():
    rows = rows_for("a", [100] * 5, owner="Adelaide")
    rows[-1] = ForecastValueRow(
        player_id="a",
        forecast_year=2031,
        expected_utility=100,
        uncertainty=0,
        current_owner="Brisbane",
    )
    with pytest.raises(ValueError, match="conflicting"):
        build_export_rows(rows, forecast_years=YEARS)
