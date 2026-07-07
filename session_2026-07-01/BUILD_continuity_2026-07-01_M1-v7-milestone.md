# BUILD continuity checkpoint — 2026-07-01 — M1 + refined-v7 milestone (nothing baked)

Authoritative session state so this can resume if the chat ends. head 8aed420a / store 644d1254. NOTHING baked, no re-cut.
Canonical frozen = e0ac9c377d1e. Store pre_stage0 = 644d1254 (live). Response language English (AU).

================================================================================
CURRENT DELIVERABLE STATE
================================================================================
Completed this cycle (all measure/prototype): M1 (sustain-aware level) derived+validated; refined-v7 built and stacked on
the M1 level; combined re-check on archetypes; full 606-player backtest book; both systemic flags analysed to conclusions.
HOLDING for Luke's player reads on the Flag-A names + confirm/deny Flag-B interpretation, then the bake decision.

================================================================================
M1 (sustain-aware level selection) -- FINAL DESIGN
================================================================================
Replaces the UP-side branch of _lvl_eff_core (in _merged_recover.py). Current live branch:
    if Lc>=L_old: return L_old if (Lc-L_old)<=ft else Lc      # ft=FLAT_TOL_G 10.3/12.0/14.0
M1 branch:
    if Lc>=L_old:
        fire = (Lc-L_old)>=TOL_M1 and (exists season in last WIN yrs with games>=G_ADQ and raw avg>L_old)
        return (L_old + S_M1*(Lc-L_old)) if fire else L_old
Params (DERIVED on walk-forward, not picked): TOL_M1=5, G_ADQ=12, WIN=2, S_M1=0.46.
  Walk-forward (1996 held up-side established pts): fired n=612 sustain +3.64 fwd vs +0.68 rest; s=0.46 min-RMSE
  (stay 11.34 -> blend 10.71 < switch-to-Lc 11.56). Robust G_ADQ{10,12,14}, TOL{4-7}. Signal weak (gate AUC ~0.55) ->
  M1 is a SMALL calibrated nudge by design. Down-side/thin-career/upside-fade branches UNCHANGED.
Validation (Leff before->after): Ginnivan 71.4->74.4, Bruhn 68.9->72.4, LDU 102.1->104.5 (rise); Day 89.4 hold,
  Powell 73.9 hold. ALL CORRECT.

================================================================================
refined-v7 -- FINAL DESIGN (stacks on M1 level)
================================================================================
v7 = compress q70,q90 toward centre m=bb[2] by cB; scale q97 WIDTH by asc(age); q10/q30/q50 & tail WEIGHT untouched.
Two refinements folded in:
  (a) cB EXPOSURE-weighted: eff_seasons e = sum(min(games_s/Gcap,1)) over qual(>=6) seasons; Gcap=17 (median qual-season
      games). cB=0.47*clip((e-1)/3,0,1). Full-season players keep e~=n (original calibration preserved); thin careers e<n.
  (b) Centre = bb[2] of the band RECOMPUTED at the M1-corrected Leff. AUTOMATIC once M1 feeds cp._lvl_eff (b6 ->
      _feat_infer -> cp._lvl_eff at idx9): raising Leff lifts the whole band + its median together. No separate lagging
      median existed. asc UNCHANGED = interp(age,[20,22,24,27],[1.0,0.76,0.58,0.40]).

================================================================================
BACKTEST BOOK -- 606 players (outfield+RUC, cur>=200); COMB% = combined vs current
================================================================================
Overall mean -13.3% / median -7.5%. down>2%:375 flat:219 up>2%:12. Pctiles p5 -48.8 / p25 -20.0 / p50 -7.5 / p75..p95 0.0.
  = broad downward re-pricing (v7 compression dominant); M1 lifts 45 players, 12 materially.
Archetype: first-year -4.3/med0 (rookie-safe ✓; min from data artifacts) | rising -8.8/med-5.7 (M1 lift, but v7 nets many
  down) | plateau -15.0 (v7 target) | injury -43.5 (n=4) | decliner -16.0.
Value tier: elite -4.7 | upper -7.6 | mid -9.5 | low -18.6 (compression scales inversely w/ value = sensible shape).
Position: MID -12.2 | GEN_DEF -13.3 | GEN_FWD -9.1 | KEY_DEF -14.9 | KEY_FWD -17.9 | RUC -16.2.
Movers UP (all M1-fired genuine risers, modest): Ash +12.9, Peatling +7.2, Callaghan +6.5, Blakey +6.3, Ginnivan +6.2 ... ✓
Movers DOWN: extreme crushes are LOW-value ceiling-dominated players; several are _fut data artifacts (see below).

================================================================================
FLAG A -- trend-up but level-flat established cohort (34 players)  [OPEN: needs Luke's reads]
================================================================================
Established (n>=4), trend>=+8, level gap<5 -> M1 holds (level not elevated) and v7 shaves. Most are only MILDLY affected;
the cohort is heterogeneous. Cases warranting Luke's read (young, strong trend, materially shaved):
  Josh Ward MID a23 tr+19.1 -27.1% | Jye Amiss KEY_FWD a23 tr+15.3 -20.1% | Isaac Quaynor GEN_DEF a26 tr+17.1 -18.2% |
  Bailey Humphrey GEN_FWD a22 tr+12.5 -17.0% | Josh Rachele GEN_FWD a23 tr+15.8 -12.7% | Nic Martin MID a25 tr+11.0 -11.4%
Low-value severe crushes: Lachlan Sholl -84.1, Jack Graham -60.2, Cody Weightman -54.5.
Older noisy-uptick cases (gap flat/neg, high trend, e.g. Clayton Oliver gap-2 tr+22.9 -4.1; Luke Parker a34 tr+36.7 +0.0)
  -> level verdict (flat/declining) is more reliable than a late-career trend blip; shaves defensible.
RECOMMENDATION: trust the level (the walk-forward said trend did NOT separate sustain from regress, AUC 0.45), i.e. these
  shaves stand -- UNLESS Luke's reads flag specific names above as genuinely improving & wrongly crushed. Full 34-name list
  in _flags_support.py output.

================================================================================
FLAG B -- KEY_FWD over-compression (-17.9 mean)  [RESOLVED: very likely NOT a bug]
================================================================================
Decomposed (Cox/Amartey/King/McMahon): these low-value KEY_FWDs have value ALMOST ENTIRELY in the upper band ceiling
  (v_at_peak e.g. Cox [9,11,19,133,1024,1854]; McMahon [1,1,4,35,333,1595]). So BOTH cB (q70/q90 body) AND asc (q97 width)
  bite hard -- Cox body-27% + tail-33% = -60%; McMahon (n0,cB0) entire -58% is the asc tail cut. cB-cap barely helps
  (KEY_FWD -17.9 -> cap0.30 -16.6; worst thin cases unchanged) BECAUSE the crush is inherent to compressing a
  ceiling-dominated value -- which is v7 as-designed (same accepted principle as Ed Richards: shave speculative ceiling as
  the ~17% shot). KEY_FWD is heaviest simply because those value curves are most ceiling-dominated (boom/bust). Established
  valuable key fwds are NOT badly hit (Peter Wright -4.3, Gunston +0) -> speculative-only effect.
RECOMMENDATION: not a v7 bug; keep asc; accept speculative shaves -- UNLESS Luke flags specific ESTABLISHED key fwds as
  wrongly shaved. Deeper (out of scope) question if pursued: is v_at_peak's convexity over-valuing low-median ceilings?

MINOR -- data artifacts polluting the crush tail: gap ~ -50 with n=0 impossible level jumps (Harrison Coe, Liam Puncher,
  Mitchell Knevitt, James Tunstill) = same _fut-error class as Ryan Maric / Ed Langdon. Separate cleanup pass; NOT a v7 signal.

================================================================================
RESUME KIT
================================================================================
ENV (every run): PYTHONHASHSEED=0 RL_GAMMA=0.85 RL_PICK1=3000 RL_RUCK_TAX=0.25 RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=400
  PAR_RAMPS=22 ; PYTHONPATH=/home/claude/rl_workspace/rl_after:/home/claude/rl_vendor
LOAD (from /home/claude/rl_workspace/rl_after/): rm -f /tmp/inspect.py ; then
  g={}; exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)  under redirect_stdout. Scripts NOT named
  inspect.py. Suppress sklearn warns: 2>&1 | grep -v Warning.
Level facts: cp._lvl_eff (after merged load) = _lvl_eff_infer (hold-band); cp._lvl_eff_orig = lvl_par (=L_old, par-shrunk);
  _lvlcurr = steep-recency Lc. Levels are RAW (no era-adj). Band = b6 -> cond_prior_band -> _feat_infer -> cp._lvl_eff idx9.
  To price at a chosen level: temporarily bind cp._lvl_eff, call b6, restore (band_at() in scripts). price_band uses
  dp.v_at_peak per band node with WQ6, REPL_DROP applied.
SCRIPTS (in rl_after/): _m1_ground, _m1_calib, _m1_refine, _m1_gate (M1 derivation); _comb_recheck (archetype re-check);
  _comb_book (full book); _flags_support (Flag-A names + Flag-B cB-cap lever); _keyfwd_decomp (Flag-B driver).
NOTEPADS (in /mnt/user-data/outputs/): ..._M1-checkpoint.md, ..._combined-book.md, ..._v6-v7-unintended.md,
  ..._v6-fliers-correction.md + earlier phase notepads.

NEXT (pending Luke): (1) Luke's reads on Flag-A named cases + confirm Flag-B interpretation (or name wrongly-shaved
  established key fwds). (2) Then bake decision: M1+refined-v7 as-is, or with a Flag-A/B adjustment, or revised thresholds.
  Only on explicit "go" -> wire M1 branch + refined cB into _merged_recover.py, re-cut, re-verify panel, bump head.
