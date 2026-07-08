# TASK-020 — Contender, balanced and rebuilder horizon lenses

## Status

Implementation candidate. This task adds transparent diagnostic strategy presets. It does not select production policy or calculate real-player keeper values.

## Objective

Present the same five-season forecast distribution through three declared roster strategies without mixing strategy preference into the forecast model.

## Diagnostic presets

### Contender

- horizon weights: 50%, 27%, 13%, 7%, 3%;
- strongest immediate-production emphasis;
- risk-aversion coefficient: 0.35.

### Balanced

- horizon weights: 36%, 25%, 18%, 13%, 8%;
- central presentation with substantial immediate and near-term weight;
- risk-aversion coefficient: 0.25.

### Rebuilder

- horizon weights: 24%, 24%, 21%, 17%, 14%;
- greater medium- and longer-term weight while remaining anchored to the visible near future;
- risk-aversion coefficient: 0.18.

These are explicit initial sensitivity presets, not learned truths or final owner policy.

## Mechanism

For each horizon, the strategy lens calculates:

`weight × (expected utility − risk aversion × uncertainty)`

The annual contributions sum to the displayed strategy value. The forecast means and uncertainty inputs remain identical across all three views. No separate age or youth bonus is added.

## Behaviour

- A strong declining veteran can rank highest for a contender.
- A credible rising player can rank highest for a rebuilder because the same forecast vector improves in later seasons.
- A volatile player is penalised transparently rather than through a hidden board adjustment.
- Every displayed value can be decomposed into annual expected utility, uncertainty, penalty, weight and contribution.

## Validation

Tests verify:

- all weights sum to one;
- contender weighting is most immediate and rebuilder weighting most patient;
- all three views use one forecast vector;
- later development can outrank immediate decline for a rebuilder without a youth bonus;
- risk penalties are explicit and strategy-specific;
- annual contributions reconcile exactly;
- malformed profiles and forecast vectors fail.

## Deliberate exclusions

- No final calibration of weights or risk aversion.
- No position scarcity or roster allocation is performed in this module.
- No bench, captaincy or owner policy adjustment.
- No production release.

## Acceptance rule

Accept as diagnostic infrastructure if the three views reconcile exactly to the same underlying forecast distribution and every assumption remains visible and replaceable.