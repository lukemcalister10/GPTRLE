import pytest

from roster_ownership import (
    AUTHORITATIVE_ROSTER_RULES,
    build_ownership_records,
    is_free_agent_label,
    required_offseason_cuts,
    roster_counts,
    validate_roster_universe,
)


def test_roster_limits_are_total_46_and_offseason_40():
    rules = AUTHORITATIVE_ROSTER_RULES
    assert rules.teams == 16
    assert rules.total_list_max == 46
    assert rules.offseason_list_max == 40


def test_free_agent_spelling_and_case_are_normalised():
    assert is_free_agent_label("Free Agents")
    assert is_free_agent_label("Free agents")
    assert is_free_agent_label(" free   agent ")
    assert not is_free_agent_label("Adelaide")


def test_ownership_records_separate_named_rosters_and_free_agents():
    rows = [
        {"stable_player_id": "a", "AFFL Team": "Adelaide"},
        {"stable_player_id": "b", "AFFL Team": "Free Agents"},
        {"stable_player_id": "c", "AFFL Team": "Free agents"},
    ]
    records = build_ownership_records(rows)

    assert records[0].team == "Adelaide"
    assert records[0].is_free_agent is False
    assert records[1].team is None
    assert records[1].is_free_agent is True
    assert roster_counts(records) == {"Adelaide": 1, "FREE_AGENTS": 2}


def test_named_rosters_up_to_46_are_valid():
    rows = []
    for team_index in range(16):
        team = f"Team {team_index + 1}"
        for player_index in range(46):
            rows.append(
                {
                    "stable_player_id": f"{team_index}-{player_index}",
                    "AFFL Team": team,
                }
            )
    rows.append({"stable_player_id": "free", "AFFL Team": "Free Agents"})
    records = build_ownership_records(rows)
    counts = validate_roster_universe(records)

    assert len([name for name in counts if name != "FREE_AGENTS"]) == 16
    assert all(counts[f"Team {index}"] == 46 for index in range(1, 17))
    assert counts["FREE_AGENTS"] == 1


def test_team_above_46_fails():
    rows = []
    for team_index in range(16):
        count = 47 if team_index == 0 else 40
        for player_index in range(count):
            rows.append(
                {
                    "stable_player_id": f"{team_index}-{player_index}",
                    "AFFL Team": f"Team {team_index + 1}",
                }
            )
    records = build_ownership_records(rows)

    with pytest.raises(ValueError, match="exceed"):
        validate_roster_universe(records)


def test_required_offseason_cuts_are_based_on_total_list_only():
    assert required_offseason_cuts(46) == 6
    assert required_offseason_cuts(45) == 5
    assert required_offseason_cuts(44) == 4
    assert required_offseason_cuts(40) == 0
    assert required_offseason_cuts(37) == 0

    with pytest.raises(ValueError, match="exceeds"):
        required_offseason_cuts(47)
