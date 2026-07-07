# SESSION SUMMARY 2026-06-29 — STEP 3-B POLE RE-LEVEL APPLIED (real engine checkpoint)
Engine 38de7a01 → **e0ac9c377d1e** (pole rescaled in par_pole). Pickle 34faa865 UNCHANGED. Stores unchanged. Stage-0, NOT baked to board.
Pre-pole engine preserved at rl_after/_merged_recover.py.PREPOLE_38de7a01.

## What changed (REAL)
Per-position pole scale in par_pole: MID 1.19/GEN_FWD .93/KEY_FWD .95/GEN_DEF 1.08/KEY_DEF 1.05/RUC 1.13.
Basis: trajectory-integrated pole (mean price6(par-synth) over development T1-5) / 2yr synth; piece-2 SHAPE kept, LEVEL rescaled.

## Gate on the re-leveled engine (REAL)
A=1096, B=1405, Cook [879,456,411,365,319] identical, proven-flat Δ=0 ON THE LIFT (Daicos 7115/Soligo 2824/Bramble 150 exact);
iso-guard rebuild ≤0.8% on proven (Ward +0.8%) — ACCEPTED (correct recompute, not a leak; ISO not frozen). First-year/unproven NOT cratered.

## Micro-calls (decided)
(a) accept iso-guard ≤0.8% drift; document as lift-Δ=0 + iso ≤0.8%, not blanket Δ=0. (b) skip realized-outcome bias cert (→ backtest book, steps 4-5).

## Remaining step 3 (batched next, mechanical)
1. Dial read-offs off the accepted evidence→weight surface (PROVEN_N/POLE_RAMP/shrinkage-c/FLAT_TOL).
2. Walk-forward validation incl. the most recent (ambiguous-year-1) cohort. Then step 4 (pick-value curve).
