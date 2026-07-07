# BUILD notepad — 2026-07-01 — WALK-FORWARD BOOK reissued (M1+v7 prototype)

Reissued the backtest book in the canonical WALK-FORWARD format. Deliverable: AFL_RL_WALKFORWARD_book_M1v7-proto.xlsx.
MEASURE-ONLY — nothing baked, no re-cut. head 8aed420a / store pre_stage0 (644d1254). It is the M1+v7 PROTOTYPE, NOT a baked head.

BUILT WITH THE CANONICAL SCRIPTS (not reinvented):
- s4_matrix_M1v7.py = the canonical walk-forward builder (s4_matrix_7147.py) with the M1+refined-v7 FIX injected before the
  ASOF loop: bind cp._lvl_eff = M1 level (sustain-aware selection) + wrap g['b6'] to apply refined-v7 to REAL players only
  (pole synthetics untouched; v7 is inert there anyway). ev -> raw_ev -> price6(b6) so the swap flows through every
  season-T value. Harness unchanged otherwise. 2649 players.
- s4_render_M1v7.py = renderer matching the requested structure (the canonical s4_render put Production in a row BELOW value
  and summarised V/Yr1 & V/DraftVal; the spec wants adjacent V|P columns and Sum(V)/Sum(P)).

METHODOLOGY:
- Walk-forward: each season-T value uses ONLY that player's scoring <=T (ASOF loop truncates scoring per year, refs set to
  Y, restores after). Same as the baseline canonical book.
- Sum-ratio, NOT mean-of-ratios, everywhere it aggregates.
- Value vs Production paired throughout.
- LEAKAGE NOTE (honest): individual scoring is <=Y truncated. The cm PRIOR is the fixed league model (trained on resolved
  careers), identical to the baseline book -> common-mode, so the baseline-vs-M1v7 COMPARISON Luke steers by is apples-to-
  apples. A stricter per-Y cohort-holdout retrain is a separate harness rebuild, not a pricing swap (and was not requested).

STRUCTURE (25 sheets):
- SUMMARY: Sum(Value)/Sum(Production) per career-year. HEADLINE row = POOLED SUM(V)/SUM(P) across all curve cohorts (2004-24)
  by career-year; then one row per cohort 2003-2025 (2003/2025 pink = reference-only). GMAX=21 career-years.
- Per-cohort 2003-2025 (23 sheets): rows = every ND+RD player (busts incl., no cherry-pick), sorted by current value; columns
  Player|Pos|Type|Pick|DraftVal | Yr1 V | Yr1 P | Yr2 V | Yr2 P | ... | Current V (V and P ADJACENT). Three totals up top:
  Sum VALUE, Sum PRODUCTION, Sum V / Sum P (sum-ratio). Yr1 V = anchor (gold). Switchers show drafted->current pos.
- POOLED: MSD/SSP/PostDraft standalone (anchor Yr1 V + current).

HEADLINE Sum(V)/Sum(P) curve (pooled 2004-24, SCAR value per adj-SC production point) — the option-premium decay:
  Yr1 21.6  Yr2 20.2  Yr3 18.4  Yr4 19.0  Yr5 19.6  Yr6 19.3  Yr7 18.3  Yr8 16.3  Yr9 14.3  Yr10 12.5  Yr11 10.8  Yr12 10.2
  (high early = value dominated by option/pedigree; decays as production catches up and careers mature).

FIX-EFFECTIVENESS VERIFIED (baseline ev -> M1+v7 ev, 2026): Ginnivan 1578->1675 (M1 fires +97); Bruhn 913->750 (M1 lift
  offset by v7 body-compression); Graham 422->168 (~-60%, v7 crush, M1 doesn't fire); Max King 511->202 (KEY_FWD ceiling
  shave). Matches the cross-sectional read -> the swap is live, not a no-op.

Scripts in rl_after/: s4_matrix_M1v7.py, s4_render_M1v7.py; matrix json s4_matrix_M1v7.json.
STATE unchanged, nothing baked. HOLD (this is Luke's steering instrument for the magnitude read + the bake decision).
