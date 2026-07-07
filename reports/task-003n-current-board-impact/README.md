# TASK-003N current-board impact review outputs

This directory is populated by the `TASK-003N current-board review` GitHub Actions workflow.

The workflow builds unchanged full-current vNext artifacts, builds TASK-003K candidate artifacts with the event-logistic substitution from PR #19, runs the 804-player current-board comparison, and uploads all generated CSV/JSON artifacts.

Expected generated files include:

- `authoritative_universe.csv`
- `current_board_annual.csv`
- `candidate_board_annual.csv`
- `annual_deltas.csv`
- `player_rollup_rank_changes.csv`
- `largest_changes.csv`
- `slice_summary.csv`
- `age30_plus_lead5.csv`
- `zero_history_players.csv`
- `validation_checks.csv`
- `manifest.json`
