# BUILD — current-season drop: 2026-specific or every-year? UNIFORMITY tests (NOTHING BAKED, bake HELD)
Head `8aed420a` unchanged. Diagnostic only.

## HEADLINE
The uniform, 2026-specific drop is **real but confined to the thin-games population** — players with **<6 games in 2026** drop **−18% to −35% uniformly across EVERY cohort**. On-field / on-pace players (≥6 games in 2026) instead follow the **natural career arc** (younger cohorts rise, older decline) — which is why the earlier Phase-1 counterfactual, testing only on-pace players, missed the effect. **Leaguewide scoring is NOT down** (falsified). The mechanism is the recency/reliability machinery interacting with mid-season thin evidence, NOT a games-count penalty and NOT lower scoring.

## TEST 2 — leaguewide scoring is NOT below 2025 (FALSIFIED)
SuperCoach per-game mean (avg-weighted by games), by year:
| filter | 2022 | 2023 | 2024 | 2025 | 2026-so-far |
|---|---|---|---|---|---|
| all g≥1 | 71.84 | 71.79 | 71.78 | 71.75 | **72.30** |
| g≥6 | 73.04 | 72.85 | 72.77 | 72.79 | **74.17** |
| established (nseas≥6) | 77.42 | 77.67 | 78.20 | 79.33 | **79.83** |
2026 is marginally **higher** at every filter → no uniform scoring-level cause. This is important: it means the drop is NOT explained by "2026 games score lower."

## TEST 1 — per-transition deltas: on-field players follow the arc (NOT a clean 2026-only uniform dip)
Mean ev %-change per year-over-year transition (players g≥6 in BOTH years):
| transition | n | mean | median | %down |
|---|---|---|---|---|
| 2022→23 | 437 | +18.6% | 0.0% | 45% |
| 2023→24 | 434 | +13.8% | 0.0% | 50% |
| 2024→25 | 432 | +50.1% | −8.6% | 56% |
| 2025→26 | 381 | +24.8% | **−12.3%** | 60% |
The median established transition has been trending negative for **two** transitions — 2024→25 (a COMPLETE season) was already −8.6%. So 2025→26 (−12.3%) is a continuation of an aging-pool trend, not a clean discontinuity.
By cohort (mean %Δ), the **younger cohorts keep RISING in 2025→26** (on-field): 2019 −3%, 2020 **+30%**, 2021 **+44%**, 2022 **+9%**, 2023 **+20%**; older decline (2016 −5%, 2017 −16%, 2018 −12%). That is the career arc, not a uniform 2026 drop.

## BOOK RECONCILIATION — the uniform 2026 signal lives in the thin-games (g<6) members
Cohort-mean ev 2025→2026 over ALL debuted members, split by 2026 games:
| cohort | all Δ% | on-field (g≥6) Δ% | **off-field (g<6) Δ%** |
|---|---|---|---|
| 2016 | −11% | −6% | **−22%** |
| 2017 | −20% | −14% | **−35%** |
| 2018 | −17% | −13% | **−29%** |
| 2019 | +6% | +20% | **−18%** |
| 2020 | +22% | +42% | **−24%** |
| 2021 | +42% | +69% | **−20%** |
| 2022 | +8% | +37% | **−18%** |
| 2023 | −2% | +21% | **−32%** |
The **off-field (g<6) column is negative for every cohort (−18% to −35%), dead uniform.** The on-field column follows the arc. Averaging both is what drags each cohort's book value down (e.g. 2023: on-field +21% but all-members −2% because off-field is −32%). **This is the uniform, 2026-specific effect** — and it survives the earlier counterfactual, which only tested on-pace players and froze their rate.

## TEST 3 — mechanism: games×recency weighting + reliability-shrunk level (why thin-2026 drops)
From `conditional_prior.py` (cont.25 rebuild): weighting is by **games × recency, NOT by season**:
- `_swt(yr,Y) = RECENCY_DECAY^max(0,Y−yr)`, decay 0.72/yr.
- "Recency-weighted **reliable game-count** = the uncertainty signal… old games decay."
- "Demonstrated level weighted by **games-in-season × recency**… reliability-shrunk level: the weighted level scaled by how much recent evidence backs it. A 5-game stint reads as [shrunk]." `LEVEL_RAMP=14` recency-wtd games to count FULLY.
**The mid-season asymmetry:** as-of round ~14, the prior (2025) season is already **fully one-year-decayed (×0.72)** while the current (2026) season is only ~60% elapsed and thin. A player with few 2026 games therefore sits in an **evidence trough** — decayed 2025 + thin 2026 → low recency-weighted reliable games → the level is shrunk → value falls. This hits **every cohort's thin members** and **only the in-progress season** (it unwinds as 2026 completes). That is the uniform + 2026-specific cause. Note weighting is by GAMES (so a full-weight-per-season artifact is NOT the cause) — the driver is the **decay asymmetry** (prior season fully decayed vs current season only partly elapsed), concentrated on thin-games players.

## TEST 4 — M1+v7 interaction (informs the bake)
Re-priced with the M1+v7 prototype (baseline in parens):
- `ed-richards` (rising MID, 13g): **3134→2552, 19% drop** (baseline 4188→2487, 41%). M1+v7 **halves the drop** by compressing his inflated 2025 rising-player peak (3134 vs 4188) — less speculative premium to lose.
- `charlie-curnow` (flat KEY_FWD, 13g): 1596→877, 45% (baseline 1849→944, 49%) — essentially unchanged.
So M1+v7 **partially mitigates on-field RISER drops** (it doesn't over-price the 2025 peak in the first place) but does **not** touch the uniform thin-2026 drop (that's the upstream recency/reliability machinery; the stuck case barely moves). **The bake is largely separable from the 2026 uniform issue** — it neither causes it nor fixes it.

## ANSWER TO THE DIRECTIVE
- **2026-specific or every-year?** BOTH, split by population. **On-field players**: a multi-year aging-pool trend (2024→25 already −8.6% median) + natural arc (younger cohorts still rise) — NOT uniform, NOT a clean 2026 discontinuity. **Thin-games (g<6) players**: a genuinely uniform, current-season-specific drop (−18% to −35% every cohort).
- **Cause of the uniform part**: the recency **decay asymmetry** (prior season fully decayed while the current season is only ~60% elapsed) + reliability-shrunk level, hitting thin-2026 players. **NOT** lower scoring (falsified), **NOT** a games-count penalty on on-pace players (Phase-1 falsified that, and this reconciles: on-pace players were the wrong population).

## FIX DIRECTION (Phase 2 — NOT designing now; Luke's read decides IF it's even wrong)
The lever is the recency machinery, not a season-fraction on an availability penalty: **prorate the prior-season recency decay by the elapsed fraction f** (don't apply a full year of decay to 2025 when only ~60% of 2026 has elapsed), or gate the reliability-shrink by f. **Inert at season end (f=1)** → the historical book/curve and the M1+v7 bake are untouched. This would lift thin-2026 members while leaving on-pace players and history alone.
**But first, the read call:** a player who has genuinely played <6 games by round 14 (injured/dropped) arguably *should* be priced lower mid-season. Is the mid-season depression of thin-games players an artifact to correct, or correct behaviour? That decides whether Phase 2 runs at all.

## BAKE
HELD per directive. M1+v7 is separable from the 2026 uniform issue (softens on-field riser drops, doesn't cause or fix the thin-games drop) → it can proceed on its own read-merits when you're ready; it does not need to wait on this.
