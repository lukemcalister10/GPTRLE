# BUILD notepad — 2026-07-01 — M1 CHECKPOINT (sustain-aware level selection: derived + validated)

Checkpointing per supervisor instruction ("if M1 throws up surprises/judgment calls, checkpoint before the full backtest").
The walk-forward surfaced a real surprise about M1's MAGNITUDE. Nothing baked, no re-cut. head 8aed420a / store 644d1254.
Scripts: _m1_ground.py, _m1_calib.py, _m1_refine.py, _m1_gate.py.

================================================================================
WHAT THE WALK-FORWARD SAYS (this reshaped the design)
================================================================================
Population: established (nq>=PROVEN_N=4) held UP-side decision points from real careers, realised forward measured
(games-wtd raw avg of next up-to-3 seasons, games>=10). n~1996. All levels RAW (engine _season_rows uses raw avg; era
drift over a 2-4y window is negligible and raw keeps units consistent with L_old/Lc).

(1) Holding is only MILDLY under-priced on average, NOT systematically wrong.
    Across all held-up points: mean(rfwd - L_old) = +1.59; |rfwd-L_old|=8.46 vs |rfwd-Lc|=8.58 (L_old marginally MORE
    accurate than Lc). 45% exceed L_old+3 but 33% fall below L_old-3. => M1 is a targeted subset correction, not a re-level.
(2) The improvement signal is WEAK. Best separator of "will sustain" AUC ~0.55 (barely above the current gap gate 0.568).
    Within real-rise (rise>=5) NOTHING further separates sustain from regress (consistency AUC 0.454 - worse than random).
(3) But a REAL RISE does sustain, monotonically: full-season rise[5,8)->+2.94 fwd, [8,12)->+4.42, [12+)->+5.51
    (best-2: +5.06/+6.63/+7.85). So a CONSERVATIVE nudge for clearly-rising players is justified.

DESIGN PIVOT: a full-season-only reliability level INVERTS the validation set (fires Powell, holds the improvers) because
it excludes the current 2026 partials (all 13g < 14g) - and those partials are load-bearing:
  Ginnivan/Bruhn/LDU 2026 partial ABOVE L_old (still rising) ; Powell 2026 8g@67.6 BELOW (stalled) ; Day 2025/26 6g/2g
  (too thin to confirm). The engine's EXISTING Lc already includes partials and captures this. Core problem = FLAT_TOL
  (10-14) set too high, holding genuine +5-8 improvers.

================================================================================
M1 DESIGN (all params DERIVED, not picked)
================================================================================
UP-side branch of _lvl_eff_core, replace:
    if Lc>=L_old: return L_old if (Lc-L_old)<=ft else Lc          # current: high hard threshold, full switch
with a composite gate + partial blend:
    FIRE iff  (Lc - L_old) >= TOL   AND   exists season in last 2y with games>=G_ADQ and avg>L_old
    on FIRE:  Leff = L_old + s*(Lc - L_old)      (partial release)
    else   :  Leff = L_old                        (hold, unchanged)

Derived params:  TOL=5,  G_ADQ=12,  window=2y,  s=0.46.
Walk-forward support (G_ADQ=12,TOL=5): FIRED n=612 mean(rfwd-Lo)=+3.64 vs held-rest +0.68.
  blend s=0.46 minimises forward RMSE: stay-at-Lo 11.34  ->  blend 10.71  <  switch-to-Lc 11.56.
  (Fully switching to Lc is WORSE than doing nothing; partial nudge is the right move.)
  Robust across G_ADQ in {10,12,14} and TOL in {4,5,6,7} (higher TOL = fewer fired, higher mean fwd).
  Composite-gate AUC 0.553 (~ raw gap 0.568): this is a calibrated conditional adjustment, not a classifier - the point
  is the fired group sustains materially higher (+3.64 vs +0.68) and the partial blend is the min-RMSE response.

VALIDATION (Leff before -> after), ALL 5 CORRECT:
  Ginnivan        Lo 71.4  Lc 78.0  gap +6.6  FIRE   71.4 -> 74.4  (+3.1)
  Bruhn           Lo 68.9  Lc 76.4  gap +7.5  FIRE   68.9 -> 72.4  (+3.5)
  Davies-Uniacke  Lo102.1  Lc107.3  gap +5.2  FIRE  102.1 ->104.5  (+2.4)
  Will Day        Lo 89.4  Lc 98.7  gap +9.3  hold   89.4 -> 89.4  (0.0)   <- recent-adequate gate catches thin 25/26
  Tom Powell      Lo 73.9  Lc 75.7  gap +1.8  hold   73.9 -> 73.9  (0.0)   <- low gap (26 regression drags Lc)

================================================================================
TWO FACTS FOR SIGN-OFF BEFORE I WIRE IT / STACK v7 / PRINT THE BOOK
================================================================================
1. M1 is a SMALL calibrated nudge (+2.4 to +3.5 Leff for improvers), NOT a re-level. Walk-forward says true under-pricing
   ~+3.6 SC and the signal is weak (AUC ~0.55); moving LDU to his Lc (107.3) rather than 104.5 is WORSE out-of-sample.
   If the intent was for improvers to jump substantially toward recent form, this won't - and shouldn't.  ** CONFIRM the
   modest magnitude is the intended behaviour (or specify a different TOL / blend). **
2. Interactions:
   - M1 also slightly pulls DOWN the few players currently above FLAT_TOL (they get a full Lc-switch today; partial blend
     is more accurate). Data-supported (RMSE), but a scope note.
   - Because M1 lifts the compression CENTRE only ~+3 for improvers, it will PARTIALLY (not fully) relieve v7's improver
     over-shave (Graham -60%, LDU -8.8%). The combined re-check will quantify the residual.

HOLDING for go-ahead to: (a) wire M1 at these params (or revised), (b) stack refined-v7 (centre = M1-corrected level;
exposure-weighted cB), (c) print the combined M1+v7 backtest book. Nothing baked.
