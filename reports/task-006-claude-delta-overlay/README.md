# TASK-006 Claude delta overlay

## Result

TASK-006 passed all frozen gates.

The implementation preserves Claude's existing keeper-utility and year-6+ treatment, then transfers only the marginal five-year value difference between the TASK-003Q-fed and unchanged current-vNext-fed boards. It does not multiply survival again and does not replace the year-6+ forecast.

## Current-board checks

- authoritative players: 804
- top-100 overlap with Claude: 99
- mean absolute rank movement from Claude: 1.56
- maximum absolute rank movement: 33
- TASK-003Q marginal direction preserved: 100%
- total value error: 0

Capital shape was preserved:

- Claude top-100 share: 47.395%
- TASK-006 top-100 share: 47.310%
- Claude bottom-half share: 10.125%
- TASK-006 bottom-half share: 10.190%

For comparison, the rejected direct five-year board placed 85.268% in the top 100 and only 0.047% in the bottom half.

## Interpretation

The large TASK-004 distortion came from replacing Claude's keeper-utility architecture with direct five-year surplus pricing. It did not come from TASK-003Q's forecast change. A marginal forecast overlay incorporates the validated TASK-003Q signal while retaining the incumbent keeper-asset allocation.

## Evidence

Workflow run `28909797978` passed end to end. Artifact digest: `sha256:35f253042cc208c25a9f8a0a83be78f11bc6526354d8058c72d347e8abc33e95`.
