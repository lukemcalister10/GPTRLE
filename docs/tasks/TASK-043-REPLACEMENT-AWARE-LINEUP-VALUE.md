# TASK-043 — Replacement-aware lineup value

## Status

Accepted diagnostic infrastructure. No production board, forecast or frozen Claude file changed.

## Hypothesis

Raw expected player season points undervalue elite players who miss games because it treats every missed game as zero. In the keeper league, unavailable players are replaced by a legal emergency or reserve who still scores.

The correct immediate-production contribution is therefore:

`expected active games × (conditional player average − replacement average)`

This is equivalent to:

`expected lineup points with player − replacement-only lineup points`

where missed games receive replacement scoring.

## Replacement benchmark

For this first league-wide diagnostic, each annual position replacement average is the best unselected legal player after optimising the complete 368-slot scoring lineup on conditional average.

A multi-position player uses the lowest replacement hurdle among current eligible positions. This is an asymmetric eligibility benefit rather than a generic DPP bonus.

The replacement benchmark is diagnostic. It must eventually be recomputed from the complete legal reserve and emergency model rather than frozen.

## Xerri case study

Using the existing accepted forecasts, which still regress Tristan Xerri's 2027 conditional average to an implausible 87.6:

| Player | Balanced raw expected-points value | Balanced replacement-aware value | Raw rank | Replacement-aware rank |
|---|---:|---:|---:|---:|
| Tristan Xerri | 630.41 | 169.62 | 252 | 151 |
| Logan McDonald | 500.13 | 57.78 | 307 | 274 |
| Alex Davies | 408.00 | 48.81 | 353 | 284 |

Replacement-aware ratios become:

- Xerri / Logan McDonald: 2.94×;
- Xerri / Alex Davies: 3.47×.

The ratio becomes materially more credible even before repairing Xerri's underlying conditional-average forecast.

## Why it works

A 120-average player who plays 16 of 20 games with a 70-point replacement contributes:

`16 × (120 − 70) = 800 points above replacement`

A 100-average player who plays all 20 contributes:

`20 × (100 − 70) = 600 points above replacement`

Raw season totals would incorrectly prefer the durable player, 2,000 to 1,920, because they omit the 280 replacement points scored in the elite player's four missed games.

## Boundary found

If negative annual contributions are clipped to zero to represent the rational choice not to start a below-replacement player, 316 current players have zero five-year lineup contribution.

That is not evidence they are identical keeper assets. It means they are not currently forecast to improve a scoring lineup above the replacement benchmark.

Their remaining value can come from a separate future option component:

- probability of developing above replacement;
- future ceiling distribution;
- trade or retention optionality;
- eligibility flexibility.

Those components must not be hidden inside immediate lineup output.

## Decision

Accept replacement-aware marginal lineup contribution as the correct production quantity.

Reject raw expected season points as the primary keeper-utility quantity.

Do not use pure clipped value above replacement as complete keeper value. The next hypothesis must add a separate, non-duplicative future option component for players below current replacement.

## Guardrails

- Do not alter the forecast model in this task.
- Do not tune to Tristan Xerri or any named player.
- Do not add position-wide scarcity premiums on top of a replacement benchmark without proving they are not double counted.
- Preserve current official eligibility and recompute replacement levels after updates.
- Keep immediate lineup contribution and future keeper option value separately visible.