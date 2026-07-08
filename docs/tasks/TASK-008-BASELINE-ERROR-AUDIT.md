# TASK-008 — Unchanged-Claude baseline-error audit

## Status

Diagnostic task. No model or utility change is authorised by this PR.

## Objective

Create a deterministic, full-population audit of the unchanged Claude board before testing any remedies. The audit must isolate the six identified defect families:

1. partial-season exposure;
2. pedigree persistence after substantial AFL exposure;
3. zero-history differentiation;
4. established low-ceiling players;
5. pathological exact-zero forward values;
6. broader baseline/error integrity, including non-finite values, value floors and tied ranks.

## Governing constraints

- `engine/rl_after/` and all manifest-frozen Claude files remain byte-identical.
- TASK-006 is merged repository history but is release-blocked and must not be used as the audited value.
- The workflow generates `engine/rl_after/rl_app_data.json` directly and audits that unchanged board.
- When a TASK-007 package is supplied for independent review, the script explicitly selects `claudeV`, never final TASK-006 `v`.
- No named-player rule, player-order gate, model fit, target change or validation-protocol change.
- Every later model PR must address one hypothesis only and reproduce this audit alongside locked historical evidence.

## Definitions

These are audit definitions, not final modelling rules:

- **Partial-season observed:** the board marks 2026 evidence and contains a current-season track average.
- **Pedigree persistence:** positive `pedDecay` after at least 50 career AFL games; also report 100+ games.
- **Established low ceiling:** at least 50 career games and current Claude peak estimate `pn < 65`.
- **Established below zero-history median:** at least 50 career games and Claude value below the median zero-history value.
- **Pathological forward zero:** exact zero in `vP1` or `vP2`.
- **Value floor:** Claude value at or below 1.

The thresholds create reproducible diagnostic cohorts. They do not encode player-specific acceptance targets.

## Required outputs

- `summary.json`;
- `cohort_summary.csv`;
- `player_audit.csv`;
- focused CSV slices for each defect family;
- a GitHub Actions artifact;
- tests proving that TASK-006 values are ignored when `claudeV` is present.

## Acceptance

- unchanged Claude export completes;
- frozen-file manifest passes;
- exactly one row per legacy player key;
- every required field is present or the audit fails closed;
- no silent row drops;
- vNext test suite passes;
- generated handover is current;
- report explicitly ranks the next one-hypothesis experiments without promoting any model.
