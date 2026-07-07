# Morning Decision Brief

## Registry status

The vNext authoritative registry is now the critical-path identity spine. PR #27 has been merged into `vnext` and locks the known Max King / Maxwell King identity hazard, adds identity-health validation, adds regression tests, and documents the registry contract.

The registry contract requires downstream tooling to consume `reports/task-002-active-universe/authoritative_universe.csv` or a documented immutable derivative. Display names are labels only and cannot be primary joins.

## Known identity exception

The Max King / Maxwell King duplicate-name hazard is no longer an informal note. It is a release-gate case:

- `max-king-stk`: St Kilda Max King, born `2000-07-07`, 2018 national draft pick 4.
- `max-king-syd`: younger Max/Maxwell King, born `2007-01-09`, 2025 national draft pick 49.

Any future registry/current-board adapter must fail if these records collapse or if either row inherits the other player's birth/draft/history evidence.

## PR status

| PR | Status | Decision |
| --- | --- | --- |
| #27 | merged into `vnext` | Registry hardening complete. |
| #26 | merged into TASK-003K stack | Age-30+ lead-5 adjudication workflow added to the stack; not merged directly to `vnext`. |
| #25 | open draft | Do not merge yet. Ordinary workflows are green, but the independent-validation workflow is not visible on the head-SHA run list. |
| #24 | open draft | Do not merge yet. Current-board impact scaffold exists, but the PR body still documents an inconclusive candidate-artifact blocker. |
| #23 | closed unmerged | Superseded by #26. Keep closed. |
| #20 | open draft | Keep open until #25 is independently verified or replaced. |
| #19 | open draft | Do not merge. Requires user/model-acceptance decision. |
| #17 | open | Defer unless needed for Claude-vNext diagnostics. |
| #18 | open draft | Defer unless needed for zero-history feature planning. |

## CI / evidence notes

- PR #27 was merged only after the registry hardening branch had green relevant CI.
- PR #26 was merged only into the TASK-003K stack after its dedicated workflow and CI were green.
- PR #25 remains blocked because the workflow added by that PR is not visible in the fetched workflow runs for its head SHA; absence of the key validation workflow means the replacement for #20 is not yet proven.
- PR #24 remains blocked by the artifact-availability issue documented in the PR body.

## Ready for Claude integration

Ready now:

- authoritative registry contract;
- stable-ID join rules;
- Max/Maxwell locked exception;
- side-by-side output schema requirements;
- validation gates for a diagnostic Claude-vNext adapter;
- shortest critical path to a visible comparison.

Not ready yet:

- a proven current vNext five-lead export artifact for all 804 authoritative players, with data dictionary and hash;
- a Claude current-board export carrying `stable_player_id` or bridgeable `legacy_key`;
- a validated diagnostic join artifact showing Claude original vs raw vNext vs hybrid candidate.

## Shortest next actions

1. Regenerate the authoritative registry and confirm `identity_health_issues.csv` has no critical rows.
2. Identify or export the current vNext five-lead forecast for all authoritative players.
3. Export the Claude current board with stable IDs or legacy keys.
4. Run a diagnostic-only join validator that produces coverage checks, row-count checks, value/rank deltas, and largest disagreements.
5. Review the blinded comparison before any hybrid formula or production change.

## Risk register

| Risk | Mitigation |
| --- | --- |
| Identity collapse | Stable-ID primary joins and Max/Maxwell regression tests. |
| Name-only joins | Adapter should fail if `player_name` is used as the sole key. |
| Leakage | Registry current ownership/eligibility cannot feed historical snapshots. |
| Double fade / double survival | Classify every forecast field as conditional, unconditional, probability, quantile, or value-layer before combining. |
| Zero-history false positives | Compare zero-game players separately before accepting any hybrid board. |
| Old-player lead-5 regression | Keep PR #19 draft until age-30+ lead-5 evidence is accepted or rejected. |
| Schema drift | Require data dictionaries and hashes for Claude and vNext exports. |
| Current-board row-count drift | Fail if comparison coverage differs from the authoritative registry without a documented derivation. |
| Model/value coupling | Keep forecast diagnostics separate from keeper-value formula tuning. |

## Recommended morning decision

Proceed to a diagnostic Claude-vNext side-by-side export only. Do not merge PR #19, do not tune the keeper-value formula, and do not alter production board behaviour until the identity-safe comparison tables are reviewed.
