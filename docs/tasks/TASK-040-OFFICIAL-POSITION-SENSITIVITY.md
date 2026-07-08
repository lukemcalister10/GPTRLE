# TASK-040 — Official-position sensitivity gate

## Status

Accepted with a dynamic-scarcity interpretation. No production board, forecast or frozen Claude file changed.

## Objective

Test whether the positive-risk, budget-conserving scarcity layer responds plausibly to small official eligibility changes rather than producing arbitrary board-wide instability.

The tests alter players near the balanced replacement boundary rather than only elite players.

## Baseline scarcity budgets

| Lens | KDEF | RUC |
|---|---:|---:|
| Contender | 260.61 | 52.63 |
| Balanced | 231.54 | 19.96 |
| Rebuilder | 358.21 | 103.28 |

## KDEF supply additions

KDEF was added sequentially to James Sicily, Karl Amon, Luke McDonald and Cameron Zurhaar—GDEF-eligible players near the relevant market boundary.

Balanced KDEF budget:

- baseline: 231.54;
- one addition: 171.97;
- two additions: 119.28;
- four additions: 49.98.

The response is strong and monotone, but four useful additions do not entirely eliminate KDEF scarcity.

## RUC supply additions

RUC was added sequentially to Harrison Petty, Noah Balta, Harry McKay and Jordan Croft—tall-position candidates near the replacement boundary.

Balanced RUC budget:

- baseline: 19.96;
- one addition: 19.96;
- two additions: 19.96;
- four additions: 4.69.

The first additions are non-binding because they do not improve the optimal allocation. Once enough useful supply is added, the shallow RUC constraint is largely removed.

## Eligibility removals

Removing useful KDEF eligibility from Harrison Petty, Noah Balta, Leek Aleer and Brennan Cox increases the balanced KDEF budget to:

- one removal: 294.47;
- two removals: 375.91;
- four removals: 564.57.

Removing useful RUC eligibility from Jake Riccardi, Peter Wright, Campbell Gray and Lachlan Blakiston increases the balanced RUC budget to:

- one removal: 80.41;
- two removals: 132.66;
- four removals: 154.27.

These movements are directionally correct and material.

## Cross-position effects

KDEF and RUC budgets can change slightly when the other position's supply changes. This is expected because all constrained positions interact with the same 80 unrestricted scoring slots. The optimiser reallocates the entire league rather than pricing each position in isolation.

The cross-effects remain interpretable and are not assignment-label artefacts.

## Decision

Accept position sensitivity as a feature of the model.

Do not freeze:

- positional premiums;
- replacement lines;
- pivotal-player sets;
- scarcity budgets.

Every official position update must trigger a full scarcity recomputation. Every published board must record the exact eligibility snapshot and the KDEF/RUC budgets used.

## Guardrail

A large scarcity change after a real eligibility update is not automatically a defect. It becomes a defect only if the direction is inconsistent with the supply change, if assignment labels alter the answer without changing constraints, or if scarcity overwhelms intrinsic player value.

## Acceptance rule

Accepted because additions reduce scarcity, removals increase scarcity, non-binding additions correctly have no immediate effect, and the response is economically interpretable across all three strategy lenses.