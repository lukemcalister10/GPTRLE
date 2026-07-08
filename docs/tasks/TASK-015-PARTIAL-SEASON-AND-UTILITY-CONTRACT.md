# TASK-015 — Partial-season evidence and keeper-utility contract

## Status

Decision contract ready for implementation. This task does not alter a forecast, utility score, export or production board.

## Purpose

Translate the owner decisions following TASK-014 into executable modelling contracts before testing a new hypothesis.

## Track A — current partial-season evidence

The available 2026 player data is observed at different points between rounds 14 and 24. It is recent and useful, but incomplete.

Required treatment:

1. Separate performance when selected from availability/selection evidence.
2. Express observed performance as rates where appropriate; preserve actual games as exposure.
3. Shrink small-sample current performance toward the accepted prior forecast.
4. Use asymmetric evidence weights: positive demonstrated selection/performance may update faster than missed games impose a negative availability adjustment.
5. Do not interpret games played divided by scheduled rounds as a direct forecast weight or full-season availability estimate.
6. Do not automatically project every player to a common completed-season games total.
7. Retain uncertainty so a strong four-game sample can improve scoring upside while remaining uncertain and carrying a separate availability concern.
8. Keep the first implementation to one explicit weighting/shrinkage hypothesis and compare it with the accepted TASK-009 + TASK-012 stack.

Historical annual data cannot validate a round-specific availability curve directly. Therefore the first implementation must distinguish:

- parameters that can be validated from historical completed-season outcomes;
- present-season exposure rules that are sensitivity-tested rather than presented as learned truth;
- future work that becomes possible when round-by-round snapshots are accumulated.

## Track B — keeper utility

League facts:

- 16 teams;
- 42 players during the season;
- each roster is reduced to 37 in the offseason;
- no salary, contract or draft-round retention cost;
- clubs may pursue contender, balanced or rebuilder strategies.

Required output lenses:

- **Contender:** greatest weight on immediate and near-term marginal roster production.
- **Balanced:** central multi-year valuation with strong near-term weight.
- **Rebuilder:** greater medium-term weight, but still anchored to demonstrated production and plausible development rather than a generic youth bonus.

Required utility mechanism:

1. Use the current official position eligibility set for every forecast season.
2. Recalculate utility whenever official positions change; never project future eligibility.
3. Optimise legal starting, utility and bench allocations instead of assigning fixed replacement ranks by position.
4. Calculate a player's marginal roster value by removing the player, re-optimising, and measuring lost risk-adjusted production.
5. Let dual-position value emerge from the feasible allocation. It may be asymmetric or zero.
6. Represent bench players by expected coverage and future use, not by counting all projected points as active lineup production.
7. Derive annual scarcity from the player pool and roster constraints present at the valuation date.
8. Keep forecast output, utility, and any owner-facing policy adjustment as separate auditable fields.

## Next implementation sequence

1. Audit the repository's position, lineup and roster-rule inputs and document missing league constraints.
2. Build a deterministic roster optimiser with synthetic tests covering positional scarcity, surplus midfielders, asymmetric dual-position value and roster removal/re-optimisation.
3. Produce contender, balanced and rebuilder marginal-utility outputs from the same forecast distribution.
4. Compare explicit utility with the current reduced-form utility formula without changing production.
5. Separately test one partial-season evidence-weighting hypothesis against the accepted forecast stack.

## Guardrails

- TASK-006 remains ineligible for release or promotion.
- Frozen Claude production files remain unchanged.
- No current-player intuition is an acceptance gate.
- No model or utility implementation is promoted by this contract alone.
- One modelling hypothesis per subsequent pull request.