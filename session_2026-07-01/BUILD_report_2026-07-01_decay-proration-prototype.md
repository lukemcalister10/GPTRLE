# BUILD — decay-proration (Phase 2) PROTOTYPE — INERT holds, but the fix does NOT work as intended → HOLD
Head `8aed420a` unchanged. Nothing baked. Prototype built exactly as specified: `_swt = 0.72^max(0,(Y−yr)−(1−f))`, `f=14/24` for Y=2026, `f=1` else; rebound at inference only (models never retrained).

## BOTTOM LINE
The one safety property **holds**: the proration is a byte-exact no-op historically. But the prototype **falsifies the mechanism it was built on** and produces large uncontrolled side-effects, so it is **not viable as-is**. Recommend HOLD + a re-diagnosis before any further design. This is the prototype-before-bake discipline catching a fix that would have mispriced a third of the on-pace board.

## VALIDATION RESULTS
### 1. INERT at f=1 — PASS (byte-identical historical)
60 established players × as-of years 2022–2025: **max |Δ| = 0, #changed = 0**. Every historical valuation is unchanged → the walk-forward book's historical columns + the M1+v7 curve are untouched by construction. **The bake stays separable.** (This is the only property that behaved as intended.)

### 2. Thin-2026 lift — FAILS (mechanism inactive for 90% of thin players)
| player | 2025 | 2026 | ev26 before→after | lift |
|---|---|---|---|---|
| thomas-liberatore | 23g/111 | 4g/106 | 1455→1455 | **+0%** |
| reilly-o-brien | 25g/94 | 1g/8 | 692→692 | **+0%** |
| toby-nankervis | 22g/98 | 2g/110 | 1744→1733 | −1% |
| connor-rozee | 21g/105 | 2g/80 | 2679→2866 | +7% |

The mechanism line is the tell: for liberatore, **exposure rose 55→62.5 but the reliability-shrunk level was UNCHANGED (106.4→106.4)** — because his exposure (55) is already far above `LEVEL_RAMP=14`, so `min(1, exp/14)` was saturated at 1.0 and stays there. **Only 6 of 62 thin-2026 players (10%) are actually in the shrink regime** (exposure <14; median exposure across thin players = **35**). The diagnosed "evidence trough" assumed thin-2026 ⇒ low exposure, but exposure is *cumulative* recency-weighted games — a thin current season on top of full prior seasons still totals ~35. So the proration's intended channel (raise exposure → less shrink) is inactive for 90% of the population it was meant to fix. The only movement is a secondary `_lvl_wt` re-weighting that fires on the 2025-vs-2026 avg gap (rozee lifts, liberatore doesn't) — not on games-thinness.

### 3. On-pace players — FAILS the <2% constraint badly (35% move >2%, some ±20%)
Of 121 on-pace players (11–14g), **42 (35%) move >2%.** Biggest movers:
`jack-ross +22.2%` (78→98), `james-jordon −21.5%` (**dead-flat 63→63**), `blake-hardwick −13.0%` (75→78), `cameron-rayner −9.8%`, `james-rowbottom −9.1%`. Median |move| is 0.9%, but the tail is severe and **bidirectional**. `james-jordon` is the clincher: a flat-rate player moving −21.5% cannot be a "toward-2025" level shift — it's the proration re-weighting his *entire* season history (earlier lower seasons now count more) and propagating nonlinearly through the trained quantile models. The lever perturbs the whole Y=2026 recency feature set, so each player's move depends on their full trajectory shape — the opposite of a targeted thin-season correction.

## ROOT CAUSE
Two compounding facts kill this lever:
1. **The diagnosis over-attributed the g<6 drop to reliability-shrink.** Only ~10% of thin-2026 players are shrunk; the rest retain high cumulative exposure. For established thin-2026 players (liberatore, o-brien) the as-of-2026 drop is essentially the **forward model reacting to +1 tenure / +1 age** (correct aging) plus a tiny level move — not a recency artifact the decay clock can fix.
2. **`_swt` is a global recency lever, not a thin-season lever.** Proraring it reweights every prior season for every Y=2026 valuation, and the trained models turn that into large, bidirectional, trajectory-dependent moves.

## RECOMMENDATION (nothing baked; HOLD)
Do **not** proceed with the decay proration as specified. Options, in order of preference:
- **(A) Re-diagnose first.** Decompose the g<6 cohort drop into its channels — age/tenure (forward model) vs level vs exposure/shrink — before designing any fix. The prototype strongly suggests most of the established-thin drop is correct aging, i.e. a smaller genuine artifact than assumed. If Luke's reads flag specific thin players as mispriced, target those cases and trace their actual driver.
- **(B) If a genuine artifact remains, it's confined to the ~10% true-thin-CAREER cases** (exposure <14: rookies, long-absence returnees). A controlled lever would prorate the decay **only inside the exposure/shrink term**, and **only when exposure < LEVEL_RAMP**, leaving `_lvl_wt` on the original `_swt` — this removes the on-pace over-correction. But its reach is small and it does NOT explain the broad uniform drop, so (A) should come first.

## SEPARABILITY (unchanged)
The M1+v7 bake remains fully separable and unaffected — the proration's inert-at-f=1 property is confirmed regardless of the above. M1+v7 can proceed on its own read-merits whenever you greenlight it.
