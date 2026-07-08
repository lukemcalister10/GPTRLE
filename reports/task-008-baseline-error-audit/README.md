# TASK-008 unchanged-Claude baseline audit

Diagnostic only. No model is promoted.

The committed summary was generated from the merged TASK-007 evidence package while explicitly selecting `claudeV`; the CI workflow independently regenerates the raw unchanged Claude board and requires the audit value field to be raw `v`. This dual path proves the forbidden TASK-006 overlay is not an audit dependency.

Key counts:

- 804 players;
- 111 zero-history players;
- 312 partial-season observed players;
- 86 players with pedigree persistence after 50+ career games;
- 119 established low-ceiling players;
- 143 established players below the zero-history median value;
- four exact year +1/+2 forward zeros;
- five current value-floor rows;
- zero non-finite values.

Full `player_audit.csv` and focused slices are CI artifacts rather than committed player-specific acceptance data.
