# BUILD — partial-season proration PHASE 1 (CONFIRM): mechanism FALSIFIED → STOP before Phase 2
Head `8aed420a` unchanged. Nothing baked. Diagnostic only.

## VERDICT
**The partial 2026 game-count is NOT the driver of the across-cohort current-season drop.** Per the directive's stop-rule ("if the driver is something OTHER than the partial season, STOP and report"), I am not designing the Phase 2 proration — it would be built on a wrong basis and would barely move the board.

## The clean falsification
If the partial season were the driver, then **completing it at the same rate** (full-season games, identical avg) should restore the value toward the 2025 (complete-season) level. It does not — it recovers <10–15% of the drop, and for rate-decliners it makes the value *lower*.

## Trace 1 — rate-decline case: `rowan-marshall` (RUC, on-pace 13g)
2025 23g@105.8 → 2026 13g@**79.0**. ev 3394 → 1332 (−61%). raw_ev 3858 → 1514.
- Counterfactual 2026→22g @ same 79.0 rate: ev **1155** (LOWER than 1332), raw 1313.
- Reading: his drop is a **genuine rate decline** (105.8→79.0), correctly carried by the recency-weighted path. Adding games at the low rate makes the low level *more confident* → value falls further. There is no availability penalty here to prorate away; the partial low-rate season is already being shrunk UP toward his career prior.

## Trace 2 — flat-rate case (the clean isolation): `ed-richards` (MID, on-pace 13g)
Trajectory 2022–25: 81.9 → 86.2 → 97.2 → **111.3** (rising hard), then 2026 13g@**106.7** (essentially flat). ev 4188 → 2487 (**−41%**) with a nearly unchanged rate. raw_ev = ev (no cliff/staleness/mediocre branch fires).
- Counterfactual 2026 → 14g / 18g / 22g @ same 106.7: ev = 2486 / 2660 / **2664**. Full-season-equivalent lifts him only **+177** (2487→2664), i.e. ~10% of the 1701 drop.
- So a **COMPLETE flat 2026 season would still crater him −36%** (2664 vs 4188). The partial games account for only +177 of that. **The driver is not the partial season.**

## Flat-rate on-pace subset — full-season games does NOT recover the drop
Established, on-pace (11–14g), 2025 ≥18g, `|avg26−avg25|≤6`. `cf_lift` = value change when 2026 is set to a full 22g at the same rate:

| player | a25 | a26 | ev25 | ev26 | drop% | cf_lift(22g) |
|---|---|---|---|---|---|---|
| ed-richards | 111.3 | 106.7 | 4188 | 2487 | 41% | **+177** |
| chad-warner | 93.3 | 89.7 | 4290 | 3297 | 23% | −87 |
| noah-anderson | 113.4 | 108.1 | 5141 | 4216 | 18% | +372 |
| charlie-curnow | 69.7 | 69.6 | 1849 | 944 | **49%** | −46 |
| luke-ryan | 94.1 | 92.3 | 2284 | 1590 | 30% | −122 |
| bailey-smith | 116.4 | 122.4 | 5542 | 5122 | 8% | −649 |
| max-gawn | 127.4 | 126.8 | 2455 | 2126 | **13%** | +0 |
| nick-blakey | 101.4 | 101.3 | 3351 | 3053 | **9%** | +141 |

Two things kill the partial-season hypothesis:
1. **`cf_lift` is small and inconsistent** (often negative). Full-season-equivalent games explains only a small, uneven slice of each drop. `charlie-curnow` has a **dead-flat rate (69.7→69.6) yet drops 49%**, and games can't touch it (−46).
2. **The drop size tracks trajectory, not games.** Long-established, long-flat elites (`max-gawn` −13%, `nick-blakey` −9%) barely move; players who were **rising into their 2025 peak** (`ed-richards` −41%, `noah-anderson`, `charlie-curnow`) fall hard. A uniform games artifact would hit all on-pace players alike. It doesn't.

## What IS driving it (leading hypothesis, for redirection — not yet fully pinned)
The recency-weighted production path reprices when the **newest season becomes the dominant (weight-1) season**. Where 2025 was a rising/peak year, the as-of-2025 valuation carried an implicit **upward-trajectory / ceiling premium**; as-of-2026 the newest season merely *matches or slightly trails* 2025, so the "still rising" signal is gone and that premium collapses — and this happens **with a complete season too** (proven above). It is a **trend/level-sequence effect, not an availability penalty.**

This reframes the real question as a calibration/read call, NOT a partial-season fix:
- Is a ~40% reprice for a player who was rising and then went flat **correct** (the engine rightly stops paying for extrapolated growth), or **too harsh** (over-reacting to one flat season, especially a partial one)?
- If too harsh, the lever is in the **trend/ceiling machinery and the newest-season recency weight**, not a season-fraction `f` on an availability penalty.

## Recommendation
STOP Phase 2 as written. The `f`-prorated availability penalty would (a) target a component that explains <10–15% of the drop, and (b) be incoherent for rate-decliners (no penalty exists to remove; their partial season is already shrunk up). Proposed redirect: a focused trace of the **recency-weight × trajectory** mechanism on `ed-richards`/`curnow` (decompose raw_ev into level vs slope/ceilinng contribution, as-of-2025 vs as-of-2026), then let Luke's read decide whether stalled-riser repricing is too harsh — and if so, tune there.

## Small true residual (for completeness)
There *is* a minor partial-season component: for flat/rising players the newest season at partial games sits slightly below its full-season self (`ed-richards` +177, `noah-anderson` +372 at full games). If Luke still wants the board's on-pace players nudged up, that piece is real but small — but it is not the cause of the broad drop and shouldn't be sold as the fix.
