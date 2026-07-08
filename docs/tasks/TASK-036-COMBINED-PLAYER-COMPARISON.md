# TASK-036 — Combined intrinsic and scarcity player comparison

## Status

Accepted diagnostic baseline. No production board, forecast or frozen Claude file changed.

## Objective

Combine the complete TASK-031 intrinsic contender, balanced and rebuilder values with the finite TASK-035 scarcity premiums while keeping both components visible.

For each lens:

`combined value = intrinsic value + budgeted scarcity premium`

## Full 804-player result

All 804 players retain complete intrinsic values. Exactly 48 players receive positive scarcity premiums under each lens, limited to players with pivotal KDEF or RUC eligibility.

Maximum player premium:

- contender: 9.30;
- balanced: 8.27;
- rebuilder: 13.58.

Maximum absolute rank movement:

- contender: 7 places;
- balanced: 6 places;
- rebuilder: 9 places.

Largest relative rank loss for a player without a premium:

- contender: 3 places;
- balanced: 3 places;
- rebuilder: 4 places.

Top-100 membership is unchanged under every lens.

## Player-level review

The largest balanced gains are concentrated among key-defender eligible players near ranking boundaries, including Harrison Petty, Brennan Cox, Callum Wilkie, Charlie Comben, Tylar Young, Noah Balta and Lachlan Blakiston.

The movement is directionally consistent with the measured KDEF constraint. No GDEF, MID, GFWD or KFWD player receives a premium solely because of that eligibility.

No evidence was found of:

- current owner affecting value;
- a scarcity premium overwhelming intrinsic forecast value;
- a tied zero-value tail;
- large top-end ranking disruption;
- the rejected balanced GDEF artefact from TASK-032.

## Output contract

The combined comparison must expose, for every lens:

- intrinsic value;
- scarcity premium;
- combined value;
- combined rank.

The intrinsic component must remain available so any player-to-player difference can be explained rather than hidden in one opaque score.

## Decision

Accept the combined intrinsic-plus-budgeted-scarcity construction as the preferred diagnostic comparison baseline.

Do not yet promote to production. The next validation should test stability under plausible official position changes and compare the combined board with the frozen legacy board and known pathological cohorts without using named-player preferences as truth labels.

## Acceptance rule

Accepted because scarcity is finite, owner-independent, transparent, below 4.1% of any player's combined value in the current run, produces only modest rank changes and preserves the complete 804-player objective comparison surface.