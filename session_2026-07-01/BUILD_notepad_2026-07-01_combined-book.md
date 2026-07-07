# BUILD notepad — 2026-07-01 — COMBINED M1 + refined-v7 BACKTEST BOOK (measure/prototype, nothing baked)

Full deliverable: M1 (sustain-aware level) + refined-v7 stacked on the M1 level + combined re-check + the book.
head 8aed420a / store 644d1254 unchanged, NOTHING baked. Scripts: _m1_gate.py, _comb_recheck.py, _comb_book.py.
HOLD for Luke's review. Two decisions flagged at the bottom.

================================================================================
1. M1 (recap — full derivation in the M1-checkpoint notepad)
================================================================================
UP-side branch of _lvl_eff_core replaced with: FIRE iff (Lc-L_old)>=5 AND a season in last 2y with games>=12 & avg>L_old;
on fire Leff=L_old+0.46*(Lc-L_old); else hold. Params DERIVED (walk-forward: fired n=612 sustain +3.64 fwd vs +0.68 rest;
blend s=0.46 min-RMSE). Validation: Ginnivan 71.4->74.4, Bruhn 68.9->72.4, LDU 102.1->104.5 (rise); Day, Powell hold. ALL CORRECT.
It is a SMALL calibrated nudge (signal is weak, AUC ~0.55) — by design.

================================================================================
2. refined-v7 (two refinements folded in)
================================================================================
(a) cB now EXPOSURE-weighted: effective-seasons e = sum(min(games_s/Gcap,1)) over qual seasons, Gcap=17 (median qual-season
    games). cB=0.47*clip((e-1)/3,0,1). Full-season players keep e~=n (calibration preserved); thin-exposure careers get e<n.
(b) Compression CENTRE = bb[2] of the band recomputed at the M1-corrected Leff. This is AUTOMATIC once M1 feeds the level
    slot (b6 -> _feat_infer -> cp._lvl_eff): raising Leff lifts the whole band and its median together. No separate
    lagging-median variable existed; the centre already WAS the live band median.

COMBINED RE-CHECK (v7old% = old v7 on current level; COMB% = M1 + refined-v7; both vs current price):
  IMPROVERS   Graham a28  v7old -60.2  COMB -60.2   (M1 did NOT fire: gap +1.3<5; exposure-cB maxed 8 fulls) <-- SEE FLAG A
              Erasmus a23 v7old -33.8  COMB -29.0   (thin-career n3: M1 inert; exposure-cB 0.31->0.24)
              Tsatas a22  v7old -28.4  COMB -15.4   (thin n2: exposure-cB 0.16->0.00)
              LDU a27     v7old  -7.7  COMB  -5.7   (M1 fired +2.4 Leff -> over-shave shrinks) ✓
  INJURY      Davies a24  v7old -68.1  COMB -52.3   (exposure-cB 0.47->0.26 softens) ✓
  DECLINERS   Robertson   v7old -72.2  COMB -64.0   (thin: exposure-cB softened)
              Worpel a27  v7old -45.6  COMB -45.6   (declining, level unchanged; compressed ~correct)
  VALIDATION  Ginnivan    v7old -11.8  COMB  +6.2   (M1 fired; net UP) ✓
              Bruhn       v7old -43.2  COMB -19.2   (M1 fired; over-shave shrinks sharply) ✓
              Day/Powell  held ✓

Result: relief comes via TWO paths — M1 lift for level-elevated established risers (LDU/Bruhn/Ginnivan), exposure-cB for
thin/injury (Davies/Tsatas/Erasmus). Graham gets NEITHER (see Flag A).

================================================================================
3. THE BOOK — 606 players (outfield+RUC, cur>=200), COMB% = combined vs current
================================================================================
OVERALL: mean -13.3%  median -7.5%.  down>2%: 375 | flat[-2,2]: 219 | up>2%: 12.
  pctiles: p5 -48.8  p10 -37.4  p25 -20.0  p50 -7.5  p75 0.0  p90 0.0  p95 0.0
  => a broad DOWNWARD re-pricing (v7 compression dominates); M1 lifts 45 players, 12 materially.

BY ARCHETYPE                    mean    median   min     max
  first-year   n=85            -4.3     +0.0    -74.0    0.0     (median 0 = typical rookie UNTOUCHED ✓; min = data artifacts)
  rising       n=73            -8.8     -5.7    -55.5   +12.9    (M1-fired lift; but v7 still nets many risers down)
  plateau      n=236          -15.0    -10.3    -84.1    0.0     (v7's intended target)
  injury-prone n=4            -43.5    -37.3    -71.2   -28.4    (softened but still heavy; tiny n)
  decliner     n=208          -16.0    -11.8    -72.8    0.0     (compressed ~correct)

BY VALUE TIER: elite>=2500 -4.7 | upper -7.6 | mid -9.5 | low(200-700) -18.6
  => compression scales INVERSELY with value — heaviest on low-value proven-mediocre, elite protected. Sensible shape.

BY POSITION: MID -12.2 | GEN_DEF -13.3 | GEN_FWD -9.1 | KEY_DEF -14.9 | KEY_FWD -17.9 | RUC -16.2
  => KEY_FWD heaviest (-17.9). Confirms the divergence-scan key-fwd/def tail. SEE FLAG B.

BIGGEST MOVERS UP (all genuine sustained risers, modest magnitudes, all M1-fired):
  Lachlan Ash GEN_DEF gap+11.3 tr+20.9 +12.9 | Peatling +7.2 | Callaghan +6.5 | Blakey +6.3 | Ginnivan +6.2 |
  MacDonald +3.4 | Xerri +3.0 | Ed Richards +2.6 | Holmes +2.6 | Butters +2.4 | Bowey +2.3 | Treacy +2.0 ...  LOOKS RIGHT ✓

BIGGEST MOVERS DOWN (top of the crush list):
  Sholl MID tr+25.9 gap-3.0 -84.1 (Graham-type) | *Coe RUC gap-51.5 -74.0 (DATA ARTIFACT)* | *Tunstill gap-8.8 -72.8* |
  Ladhams RUC tr-28.9 -71.2 (inj+decline) | *Knevitt gap-14.5 -68.9 (artifact)* | Robertson -64.0 | Amartey KEY_FWD -62.1 |
  Max King KEY_FWD -60.4 | Cox KEY_FWD -60.4 | Graham -60.2 | ...
  => extreme crushes are LOW-value wide-band players; three KEY_FWDs in the top; two Graham-type; several *data-artifact*
     players (gap ~-50 = _fut errors, same class as Maric/Langdon) polluting the tail.

================================================================================
DECISIONS FOR LUKE (nothing baked; these change the design)
================================================================================
FLAG A — Graham cohort (34 players). Established, trend-up (>=+8) but level-FLAT (gap<5) -> M1 holds them and v7 compresses
  them hard (Graham -60, Sholl -84). The LEVEL path does not see them as rising (their recency-weighted level ~= career
  level), which DISAGREES with the short-term trend flag. So the supervisor's expected Graham fix does NOT happen: M1 is
  level-based and won't fire on trend-up/level-flat players, and their exposure-cB is maxed (genuine full seasons).
  ==> Is a player whose recency-weighted LEVEL equals his career level "really" improving? If NO, -60% is v7 as-designed
      and correct. If YES (trend should count), M1's gate needs a trend/last-season component — but the walk-forward said
      the level signal is what predicts forward, and trend within real-rise did NOT separate (AUC 0.45). Recommend: trust
      the level (hold Graham), i.e. -60% stands, UNLESS your player reads say specific names are wrongly crushed.

FLAG B — KEY_FWD over-compression (-17.9 mean, heaviest; Amartey/King/Cox all ~-60). Volatile key-fwd bands are widest, so
  v7's body-compression bites hardest. May want a position-aware cB cap or a floor for KEY_FWD/KEY_DEF. Needs your read on
  whether these key-fwd values are genuinely too high now or v7 is over-shaving the boom/bust upside.

MINOR — data-artifact players (gap ~ -50, n=0 with impossible level jumps: Coe, Puncher, Knevitt, Tunstill) pollute the
  crush tail; same _fut-error class as Maric/Langdon. Recommend a separate cleanup pass; they are not a v7 signal.

HOLDING for: your read on Flags A & B, then (per your call) either bake M1+refined-v7 as-is, add the KEY_FWD/trend
adjustments, or refine thresholds. Nothing baked.
