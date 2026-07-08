# TASK-021 — Asymmetric partial-season update

## Status

Accepted diagnostic infrastructure. This task adds an isolated current-season evidence adapter and sensitivity tests. It is not wired into production and does not retrain the accepted forecast stack.

## Hypothesis

Recent 2026 performance should update the prior forecast with credibility that grows with games played, while negative availability evidence should update more slowly than the raw proportion of games missed because absence is ambiguous.

Performance and availability are therefore treated separately.

## Scoring update

Scoring credibility is:

`games played / (games played + 8 prior games)`

The updated scoring rate is the credibility-weighted blend of the observed 2026 rate and the accepted prior scoring forecast.

Examples:

- 4 games receive 33.3% credibility;
- 8 games receive 50.0%;
- 12 games receive 60.0%;
- 20 games receive 71.4%.

A strong short sample can improve the player's scoring outlook, but it cannot replace the prior forecast immediately.

## Availability update

Observed availability is `games played / matches available` and is compared with the player's prior availability expectation.

Positive evidence uses:

`matches available / (matches available + 8)`

Negative evidence uses only the expected-game deficit:

`deficit / (deficit + 22)`

This deliberately makes absence weaker evidence than direct proportional weighting. The 12-of-24 example remains a sensitivity illustration: with a 100% prior availability expectation it creates a 12-game deficit and receives 35.3% negative credibility, not 50%.

For the current 2026 snapshot, all players have passed through 14 rounds and one bye, so every player has 13 possible matches. Use 13 uniformly as the availability denominator.

## Key behaviour

- A player averaging strongly in four games gains scoring upside but remains highly uncertain.
- The same player can carry a separate availability concern without the scoring rate itself being crushed.
- Zero games preserve the scoring prior while updating only availability.
- Positive demonstrated selection receives credibility faster than an equivalent negative deficit.
- Policy strengths are explicit and replaceable for sensitivity analysis.

## Validation limitation

The annual historical data cannot identify the correct intra-season credibility constants because it lacks historical round-level snapshots. These constants are therefore declared sensitivity parameters, not learned truth. They must be compared across plausible alternatives and replaced by outcome-tested estimates once round-by-round snapshots accumulate.

The previously stated need for a per-player observation round is resolved for the current snapshot: the authoritative context is uniformly 14 rounds elapsed and 13 matches available.

## Acceptance rule

Accept as isolated diagnostic infrastructure if scoring and availability remain separate, negative availability credibility remains deliberately sub-proportional, exposure errors fail explicitly and no production output changes.