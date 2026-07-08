# TASK-013 — Exact forward-zero continuity

## Status

Numerical continuity candidate. No forecast retraining, keeper-utility change or production promotion.

## Hypothesis

Exact zero in a finite future value component is a lower-bound artefact rather than a defensible claim of literally zero possible future keeper value. Replacing exact `vP1` and `vP2` zeros with the existing minimum positive board unit of 1 removes the discontinuity without changing current value, rank or any non-zero forecast.

## Single change

For finite, non-negative forward components only:

- `vP1 == 0` becomes `1`;
- `vP2 == 0` becomes `1`;
- every non-zero value and every other field remains byte-equivalent at the decoded data level.

The rule is general and contains no player names, ages, clubs, positions or ordering targets.

## Required invariants

- raw Claude output remains frozen and untouched;
- 805 raw rows reconcile to 804 authoritative players plus one legacy-only row;
- exactly seven authoritative fields across four players change on the audited board;
- no legacy-only field changes;
- no current `v`, rank or non-zero forward value changes;
- no authoritative exact zero remains in `vP1` or `vP2`;
- malformed, negative, non-finite or ambiguous input fails closed;
- TASK-006 is not an input or dependency.

This PR produces an explicit candidate board and diff artifact. It does not wire the adapter into production export.
