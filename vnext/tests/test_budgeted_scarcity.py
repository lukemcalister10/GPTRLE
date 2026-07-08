import pytest

from budgeted_scarcity import allocate_position_budget, allocate_scarcity_budgets


def test_position_budget_is_conserved_exactly():
    allocation = allocate_position_budget(
        {"a": 3.0, "b": 1.0, "c": 0.0},
        budget=40.0,
    )

    assert allocation == {"a": 30.0, "b": 10.0, "c": 0.0}
    assert sum(allocation.values()) == 40.0


def test_equal_pivotality_receives_equal_premium():
    allocation = allocate_position_budget(
        {"a": 5.0, "b": 5.0},
        budget=12.0,
    )

    assert allocation == {"a": 6.0, "b": 6.0}


def test_multiple_position_budgets_combine_without_losing_accounting():
    rows = allocate_scarcity_budgets(
        {
            "KDEF": {"dual": 2.0, "key": 2.0, "ruck": 0.0},
            "RUC": {"dual": 1.0, "key": 0.0, "ruck": 3.0},
        },
        {"KDEF": 20.0, "RUC": 8.0},
    )
    by_id = {row.player_id: row for row in rows}

    assert by_id["dual"].position_premiums == {"KDEF": 10.0, "RUC": 2.0}
    assert by_id["dual"].total_premium == 12.0
    assert by_id["key"].total_premium == 10.0
    assert by_id["ruck"].total_premium == 6.0
    assert sum(row.total_premium for row in rows) == 28.0


def test_zero_budget_allocates_zero_without_positive_weights():
    assert allocate_position_budget({"a": 0.0, "b": 0.0}, budget=0.0) == {
        "a": 0.0,
        "b": 0.0,
    }


def test_positive_budget_requires_positive_pivotality():
    with pytest.raises(ValueError, match="positive pivotality"):
        allocate_position_budget({"a": 0.0}, budget=10.0)


def test_position_sets_must_match():
    with pytest.raises(ValueError, match="exactly match"):
        allocate_scarcity_budgets(
            {"KDEF": {"a": 1.0}},
            {"KDEF": 10.0, "RUC": 5.0},
        )
