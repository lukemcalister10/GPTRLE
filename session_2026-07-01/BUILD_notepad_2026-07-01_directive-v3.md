# BUILD notepad — 2026-07-01 — Directive v3 (low-games/no-games) prototype + diagnosis

Nothing baked; head 8aed420a unchanged. Three prototype books built (M1+v7 inherited). Full write-up in
BUILD_report_2026-07-01_directive-v3-lowgames.md.

PART A — decisive, honest finding: year-1 does NOT lift under the full model; it DROPS.
  (0) M1v7 base Yr1=1067k (Yr1/Yr2-7=0.84)
  (1) +retain0.1 ONLY: 1126k, +5.6%, ratio 0.88  -> the retain-raise WORKS (moves toward plateau)
  (2) +retain +w-blend: 865k, −23% vs (1), ratio 0.72, indexed peak 146%->175% -> the w-blend BACKFIRES
  Why: only 29% of Yr1 sat out; 71% played. The unified blend pulls played 6-22g rookies from production DOWN
  toward the draft-anchor (thin-sample discount). Yr1 is NOT uniformly low — sit-outs low (retain fixes), but
  6-22g rookies are OVER-TRUSTED at full production and the blend discounts them. Luke's read decides if that's
  correct. OFFER: cliff-only-blend (blend ns==0 only) would LIFT Yr1 — build on his word.
  M1+v7 stays bake-ready; both Part-A changes PLACEHOLDER, direction-only.

C.5 Lombard: current 2026 value fine (ns=1, prod 1531). Cliff is YEAR-1 (ASOF 2025, [4g], ns=0 since nseas needs
  games>=6) -> anchor 802 (=1603x0.50), 4g production (995) discarded. Cutoff making 4==0 = the 6-game nseas
  threshold. Fix: retain-raise 802->962; w-blend +1 ->963 (small at 4g by design).

C.6 cutoffs: 6g cliff (biggest movable, aggregate = the -23%), delist gate 0.02dv (biggest, intentional),
  PROVEN_N=4/nqual>=10g, M1 G_ADQ=12/TOL5/WIN2, staleness onset, mediocre pr<0.55, cB clip, FLAT_TOL, N cap 6.

C.7 provenance: NOT a silent bug — a DOCUMENTED designed placeholder. Code header + handover: "deferred-to-PVC
  shape placeholders"; tail measured only to N5, yr3-6 designed and sits ABOVE measurement for RUC/KPP (RUC yr3-4
  +0.24/+0.22, KPP yr4-5 +0.36/+0.22; nonKPP aligned). Standing action already = re-derive on measurement, pool.
  Re-derivation (realized production/draftval, busts=0, with SAMPLE SIZE): tail thin (N>=4: RUC<=22, KPP<=36,
  nonKPP<=60; N5-6 single digits RUC/KPP). Washout rises 26%->~55%+ with N (retention should decline, steeper).
  RUC bimodal+thin (median ~0.1, mean >1 from few elite breakouts) -> mean unreliable, ceiling must be derived.
  nonKPP VERDICT: 0.50 yr1 NOT too harsh — realized ~0.37 mean / ~0 median sits BELOW 0.50 (slightly generous).
  +0.1 placeholder is WRONG-DIRECTION for KPP (widens the over-statement). Proper fix = pooled PVC-ruler
  re-derivation at the pick-curve step.

C.8 data availability: w-ramp (k-games-yr1 -> eventual-level reliability) DERIVABLE from DB (not yet done;
  prototype used principled convex G_FULL=44/WSHAPE=1.3). Within-season penalty proration NOT derivable — DB is
  season-aggregate, no round-level debut timing -> principled f=round/rounds.

PART B (live-board, doesn't move the book): penalty proration CONVEX-GENTLE retain_eff=1-f^k(1-retain); at
  f=0.5 penalty fraction k1.5/2/3 = 35%/25%/12.5% (all <50%, k=2 default). M1 gate CONVEX-HARDER required =
  G_ADQ*f^0.58; at round12/24 -> ~8 (67%), to 12 by season end. Matches Luke's calibration.

Open decisions: (1) build cliff-only-blend? (2) 6-22g rookies over-valued or fine? (3) proceed to pooled
  PVC-ruler retain re-derivation (+ w-ramp derivation alongside).
