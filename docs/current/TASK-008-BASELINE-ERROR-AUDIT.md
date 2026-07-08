# TASK-008 — Baseline-error audit

## Decision

The unchanged Claude board remains the production baseline. TASK-006 and the TASK-007 package that exports it are retained as merged experimental history but are not eligible for promotion or release.

This task is diagnostic only. It does not change a model, utility transform, board value or UI payload.

## Audited population

The audit covers all 804 authoritative players and selects the unchanged Claude value:

- raw Claude export: `v`;
- TASK-007 review package: `claudeV`, explicitly ignoring TASK-006 `v`.

## Findings

| Defect family | Full-population diagnostic |
|---|---:|
| zero-history players | 111 |
| partial-season observed players | 312 |
| positive pedigree decay after 50+ career games | 86 |
| positive pedigree decay after 100+ career games | 9 |
| established low-ceiling players | 119 |
| established players below the zero-history median value | 143 |
| exact zero in year +1 or year +2 value | 4 |
| players at the value floor (<= 1) | 5 |
| non-finite current values | 0 |
| non-finite forward/backward components | 0 |

The zero-history median unchanged-Claude value is 288. The exact forward-zero cohort is a numerical pathology, not evidence that those players have literally no possible future value.

For 312 partial-season players, the current Claude peak estimate exceeds the current-season observed average by 21.42 points on average, with MAE 22.76. This is not a target-accuracy result because the 2026 season is incomplete; it demonstrates that the current board uses a fixed progress convention and needs a historically testable exposure representation.

## Interpretation

1. **Partial-season exposure is not player-specific.** The frozen engine uses a single season fraction (`RL_M3_FE`, default 0.58). A future experiment should derive exposure from origin-safe playable/observed games rather than a calendar constant.
2. **Pedigree persists after substantial evidence.** Positive pedigree decay remains for 86 players with 50+ career games, including nine with 100+. A future experiment should test whether demonstrated AFL exposure should dominate the draft prior more quickly.
3. **Zero-history states remain weakly separated.** Existing TASK-003 diagnostics show these rows are within numeric feature support but collapse materially different prospects into similar low-information vectors. The next forecast experiment should use verified zero-AFL list tenure plus broad entry pathway/pick representation.
4. **Established low-ceiling players overlap high-value priors.** 119 players have 50+ career games but a current peak estimate below 65, while 143 established players sit below the median zero-history value. A dedicated hypothesis should test a smooth demonstrated-ceiling constraint, not named-player markdowns.
5. **Exact forward zero is a numerical failure mode.** Four rows reach exact zero in `vP1` or `vP2`, and five current values sit at the floor. This should be fixed with a general non-negative continuity invariant, separately from any football-model hypothesis.

## Experiment order

The next work remains one hypothesis per PR:

1. partial-season exposure representation;
2. pedigree persistence versus demonstrated exposure;
3. origin-safe zero-history state separation;
4. established low-ceiling demonstrated-ceiling constraint;
5. pathological-zero continuity invariant.

The ordering separates information-boundary corrections from forecast structure and numerical safety. A candidate advances only on locked historical outcomes and full-population effects, not because selected current players look more intuitive.

## Reproduction

```bash
python vnext/audit_task008_baseline_errors.py \
  --claude-board engine/rl_after/rl_app_data.json \
  --out build/task008
```

Committed compact evidence is under `reports/task-008-baseline-error-audit/`. Full player-level evidence is produced by CI.
