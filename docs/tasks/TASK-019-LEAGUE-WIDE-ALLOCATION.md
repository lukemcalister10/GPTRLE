# TASK-019 — League-wide active allocation

## Status

Implementation candidate. This task adds a scalable league-wide active-lineup allocator and diagnostics. It does not define forecast utility, bench utility, strategy weights or production keeper values.

## Objective

Allocate the full player pool across the 16 teams' 288 active positional slots using current official eligibility, then expose the active replacement structure created by the actual player pool rather than fixed positional constants.

## Mechanism

- Replicate the exact 18 active slots for each of 16 teams.
- Exclude the five bench slots from active scoring replacement lines; bench coverage is a separate utility component.
- Accept one externally supplied utility value per player.
- Solve the maximum-utility legal assignment with SciPy's rectangular assignment solver.
- Preserve multi-position eligibility, allowing the optimiser to choose the position where each player creates the most league-wide value.
- Recompute the optimum after player removal to measure marginal active utility.
- Restrict a player to primary position and recompute to measure the value of additional eligibility.
- Report assigned minimum, median and maximum utility by slot family as diagnostics, not fixed future constants.

## Why this avoids midfield overvaluation

Raw scoring is not itself replacement value. A higher-scoring midfielder can have less marginal utility than a lower-scoring general forward when another strong midfielder can take the vacated midfield slot but the available forward replacement is materially weaker.

Dual-position value is also asymmetric. A forward who gains midfield eligibility may add nothing if midfield slots are already deeper. A midfielder who gains forward eligibility may add significant value when it allows a stronger overall legal assignment.

## Validation

Synthetic tests verify:

- exactly 288 active slots from the accepted league configuration;
- equality with the dependency-free reference optimiser on small problems;
- scarce-position marginal utility exceeding a higher raw score at a deep position;
- zero FWD-to-MID flexibility value where appropriate;
- positive MID-to-FWD flexibility value where appropriate;
- exact positional assignment summaries;
- explicit failure for infeasible eligibility.

## Deliberate exclusions

- No bench multiplier or injury-cover value.
- No contender, balanced or rebuilder horizon weights.
- No risk adjustment or captaincy.
- No choice of accepted forecast field as the utility input.
- No real-player ranking or production export.

## Acceptance rule

Accept if the league-scale solver matches the reference optimiser on controlled cases, preserves current eligibility, fills all 288 active slots and fails explicitly when the pool is infeasible.