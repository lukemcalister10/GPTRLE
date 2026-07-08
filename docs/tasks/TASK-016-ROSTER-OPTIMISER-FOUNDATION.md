# TASK-016 — Roster optimiser foundation

## Status

Implementation candidate. This task adds deterministic allocation primitives and synthetic tests only. It does not calculate real-player keeper values or change production.

## Repository audit

The frozen Claude engine currently uses fixed replacement constants:

- MID 80.1;
- general defender 78.3;
- ruck 78.5;
- key defender 68.4;
- general forward 70.9;
- key forward 66.8.

Those constants are embedded in `engine/rl_after/rl_model.py` and are applied through a smooth points-above-replacement transform. The same file records that dual-position blending was removed and each player is collapsed to one present/dominant position. Consequently the production utility layer cannot measure whether a player's second position changes the best feasible roster.

The repository does contain current position fields in the player data contract, but it does not yet contain one authoritative, machine-readable league lineup configuration covering exact starting slots, utility slots, bench treatment, key-position requirements or captaincy. The comments attached to the legacy replacement constants contain historical derivation assumptions, but these are not treated as authoritative league rules.

## Added foundation

`vnext/roster_optimiser.py` provides:

- explicit player utility and current eligibility inputs;
- explicit roster-slot eligibility and utility multipliers;
- deterministic maximum-utility legal assignment;
- failure when a slot cannot be filled rather than silent omission;
- remove-and-reoptimise marginal roster utility;
- dual-position flexibility value relative to primary-position-only eligibility;
- deterministic expansion of configurable slot counts.

The optimiser uses a dependency-free min-cost-flow implementation suitable for keeper-roster sized problems.

## Synthetic evidence

Tests verify that:

1. an 80-point scarce forward can carry more marginal value than a 100-point midfielder when the available forward replacement is weaker;
2. adding midfield eligibility to a forward can have exactly zero value;
3. adding forward eligibility to a midfielder can unlock material value;
4. removing a dual-position player causes all remaining assignments to be re-optimised;
5. bench contribution is counted only through an explicit multiplier rather than full active-lineup production;
6. infeasible configurations fail explicitly.

## Deliberate exclusions

This task does not yet choose:

- the league's exact active lineup slot counts;
- bench coverage multipliers;
- contender, balanced or rebuilder horizon weights;
- risk adjustment;
- captaincy treatment;
- replacement-player construction;
- real-player utility inputs.

Those items must be introduced as explicit configuration and tested separately. The optimiser foundation does not infer them from the old fixed replacement marks.

## Acceptance rule

Accept if the implementation is deterministic, all synthetic scarcity/flexibility tests pass, and the frozen Claude manifest remains unchanged. Acceptance does not approve any keeper-value formula or production cutover.