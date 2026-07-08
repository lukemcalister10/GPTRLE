# TASK-032 — Smooth global scarcity premium

## Status

Implementation candidate. This task adds a league-wide, owner-independent scarcity adjustment to intrinsic player value.

## Hypothesis

Positional scarcity should add value where a position's global replacement line is stronger than the unrestricted scoring-slot replacement line. The adjustment should not:

- replace intrinsic forecast value;
- depend on current owner or one named roster;
- force every player outside the optimal 368 to zero;
- sum multiple position bonuses and double-count production;
- use fixed permanent replacement marks.

## Formula

For each eligible position:

`scarcity gap = max(0, position cut line − unrestricted cut line)`

The player's activation around that position is:

`logistic((intrinsic value − position cut line) / bandwidth)`

The position premium is:

`premium scale × scarcity gap × activation`

A multi-position player receives the **largest** eligible premium, not the sum of all premiums.

The combined diagnostic value is:

`intrinsic value + scarcity premium`

## Why this form

- Cut lines come from the current global 16-team, 368-slot allocation and therefore update when forecasts or eligibility change.
- The unrestricted cut line is the comparison baseline because all players can occupy those 80 scoring slots.
- Only the additional difficulty of filling a constrained slot is rewarded.
- The logistic activation avoids a hard cliff at player 368 and allows below-cut-line prospects or depth players to retain a small continuous scarcity signal.
- Taking the best eligible position preserves asymmetric DPP value without awarding a generic bonus for holding multiple labels.

## Parameters

Initial diagnostic defaults:

- bandwidth: 40 utility points;
- premium scale: 1.0.

Both are explicit sensitivity parameters and are not accepted production calibration.

## Interpretation

This is an additive **scarcity premium**, not a replacement-value score. Intrinsic production and risk-adjusted horizon value remain the main comparison signal.

A position whose constrained cut line is below the unrestricted cut line receives no premium. This prevents scarcity logic from rewarding a position merely because it has a named slot.

## Required validation

The full 804-player diagnostic must report:

- positional and unrestricted cut lines for each lens;
- premium distribution and maximum share of combined value;
- rank changes against the intrinsic TASK-031 baseline;
- whether non-selected players retain continuous nonzero values;
- DPP cases where additional eligibility adds zero or material value;
- sensitivity to bandwidth and premium scale.

## Acceptance rule

Accept only if the adjustment produces modest, interpretable rank movement concentrated around genuinely constrained positions, remains owner-independent, does not create a tied zero tail and does not overwhelm intrinsic forecast value.