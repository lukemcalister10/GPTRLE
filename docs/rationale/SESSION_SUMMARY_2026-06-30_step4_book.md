# SESSION SUMMARY — STEP 4 (pick-value curve) BOOK build + WF bug fix — 2026-06-30
Engine **e0ac9c377d1e** (pole-rescaled, calibrated), Stage-0, NOT baked. No engine change this session.

## Where we are
Step 3 CLOSED. Step 4 = pick-value curve. Sequence: build the walk-forward backtest BOOK first → Luke
eyeballs for valuation sanity → ONLY THEN compute the curve (fix any eyeball-surfaced mispricing BEFORE
it is averaged in). This session built + sent the BOOK and is HOLDING for the eyeball. Curve NOT computed.

## 1. Acquisition-type classification (CONFIRMED — mechanical)
Data = 2656 records, `type` field. Eligible after dropping `_phantom`(4)/`_double_count`(2)/`_pvc_exclude`(3).

IN the ND pick curve (continuous pick order ND pk1..last → RD pk1..last; cohorts 2004-2024):
- **ND** (1571) National Draft — incl. father-son/academy bids made VIA the national draft (they consume
  an ND pick at the bid → in-order; e.g. Harry Dean FS pk3, Zeke Uwland Academy pk2).
- **RD** (693) Rookie Draft — continuous after the last ND pick (populates the deep-pick tail).

STANDALONE pooled (one distribution-aware value each, cross-ref to curve LATER; all pickless):
- **MSD** (108) Mid-Season, anchor ~1.5 seasons. **SSP** (52) — 2 stray have-pick flagged.
- **Post-Draft family** (218): UNR/Unregistered(59), IRE/Ireland(58), PDA/Academy(51), PDN/NextGen(43),
  PDS/Scholarship(21).

Father-son/academy middle case resolves cleanly via type+pickless: ND-type FS/academy = in-order;
post-draft PDA/PDN (pickless) = standalone. OPEN JUDGMENT CALL (deferred to the equivalence/curve step):
whether the post-draft family is ONE pooled "Post-Draft" value or split by category (each n>20). Book
lists them individually, so deferrable.

Cohort flags: 2003 (no yr1 SuperCoach scoring) + 2025 (no completed yr1) = reference-only, EXCLUDED from
curve. Curve = 2004-2024 ND+RD only. Book includes 2003-2025.

## 2. Walk-forward method
Per the established `forward_valuation/build_cohort_book.py`: per YEAR Y, truncate every player's scoring to
rows ≤ Y, set `MA.BASE_REF=MA.AGE_REF=Y`, `_pe_clear()`, value all drafted ≤ Y with the NEW engine `ev()`.
This is the same `price_asof` approach validated in step 3. **Anchor = end of CALENDAR Year 1 (draft_year+1),
regardless of games played** — a sat-out draft year is a real, counted low-value year (pedigree pole), NOT
collapsed to the first played season (see §6). Trajectory = WF value as-of each calendar year since draft.
Production (P) row = era-adj season avg (0 for no-games years).

## 3. BUG CAUGHT + FIXED (mine, not the engine's) — WF delisted-floor leakage
First render showed retired stars degenerate: Deledio pk1 frozen Yr1=Yr2=Yr3=**60**, Roughead **50**,
descending by pick (60/50/45/42/39 = 0.02×draftval = the DELISTED floor). 60-75% of old cohorts hit it.
ROOT CAUSE: `delisted(p)` fires on the PERSISTENT `_retired`/`_last_listed` flags, so any player retired
NOW returned `0.02×draftval` at EVERY walk-forward year — retirement is FUTURE info leaking into past
valuations, corrupting most of the historical book (all old cohorts are now retired).
FIX (in `/tmp/s4_matrix.py` WF loop): compute `eff_last` = `_last_listed` if set else (last scoring year
if `_retired` else None = still active); per year set `p['_retired']=False` and
`p['_last_listed'] = eff_last if (eff_last is not None and eff_last < Y) else None`. I.e. **delisted as-of Y
IFF last activity STRICTLY before Y**. Active players (eff_last None) never floored; retired players show
REAL values during their careers and the floor only AFTER they left (incl. correct current floor).
(First attempt blanket-masked at all years → wrongly un-floored retired players' CURRENT value; refined to
per-Y.) Verified: Deledio V=[3449,3504,3936,4966,5009,4637] cur=60; Pendlebury [2122,3568,5001,5896,6511,
7095] cur=583; active players (Daicos/Harley Reid/Luke Jackson) unchanged; cross-cohort anchor sums smooth
(2004=48.6k … 2007=70.5k) vs the pre-fix 990/3192 artifact.

## 4. The BOOK (DELIVERABLE — sent)
`/mnt/user-data/outputs/AFL_RL_WALKFORWARD_book_2026-06-29.xlsx` — 26 sheets:
- **Summary** — per-cohort #ND+RD / #pooled / anchor sum / current sum / in-curve flag; method notes.
- **Per-cohort 2003-2025** — Luke's established FULLCLASS style: V (WF value) / P (era-adj production)
  paired rows, Yr1..YrN trajectory, sorted by current, cohort-total sum-ratio (SUMIFS), Yr1 anchor gold,
  2003/2025 tagged reference-only. ND+RD only (the curve population).
- **Pooled** — MSD/SSP/post-draft, every player named, anchor + current (mean shown for ref only; the
  equivalence will use the DISTRIBUTION-aware value, not the mean). Partial-sample flag on 2024/25 entries.
- **FLAT** — one row per player-year (player,pos,type,in_curve,pick,draft_year,season_idx,value_WF,
  is_anchor,production_adj,current) for the curve calc.
2090 ND+RD curve-anchors (2004-2024), 389 pooled.

## 5. TWO RE-RENDER FIXES (no recompute, no curve) — applied after first send
**(a) Cohort-trajectory SUMMARY view — "Cohort Trajectories" tab.** One row per cohort (2003-2025),
season-by-season. **TABLE 1 = MEASURE 1**: each year's summed V as % of the cohort's OWN end-of-Year-1
total. Denominator = the cohort's FULL Yr1 value, **FIXED across all years** (busts INCLUDED forever; they
contribute 0 to the numerator once gone) — this kills the survivor bias (the shrinking-denominator illusion
that produced the original book's false late-climb) and drops PVC/DraftVal (the retired position-blind
currency). Yr1 = 100% by construction; later years read SHAPE (build/peak/fade) vs the cohort's own start —
NOT cross-cohort quality. Verified: honest fade now (2008: Yr4 185% → Yr6 149% → Yr8 99% → Yr10 55% → ~0
fully retired), Yr1=100% every cohort. **TABLE 2** = absolute summed V (SCAR), kept as reference.
**MEASURE 2** (cross-cohort quality vs the UNIVERSAL PVC: denominator = sum of curve PVC[pick] over the
cohort's actual picks, ~constant across cohorts → surfaces genuinely strong/weak classes, e.g. weak 2020
below 100%) is FLAGGED ready-to-add but GATED on the curve existing — built NEXT, not now.

**(b) Retired players' CURRENT = 0, not the delisted floor** — Current was showing `0.02×DraftVal` (the
`delisted()` floor: Cooney pk1=60, Walker pk2=50, descending by pick) for retired players, inflating
current sums (2003 read 1283 with ZERO active players). The TRAJECTORY cells were already correct (retired
players' post-career years blank, since Vpath holds played seasons only) and the CURVE is unaffected (reads
the Yr1 anchor). So this was an isolated current-column artifact. FIX: `retired_now` = the agreed
listed-window rule's output = `delisted(p)` at 2026 (`_retired` OR `_last_listed`<2026 — the materialized
flag) **PLUS** a direct veteran catch for players the source flag hasn't updated: drafted ≤2021 (longest
~4-season min-window elapsed by 2025) AND no game in 2025/2026 → retired. Current = 0 when `retired_now`,
else real value. Verified: 2003/2004/2006 → 0 (all retired); 2005 → 583 (Pendlebury correctly LEFT active —
he played 2025, the rule rightly does not zero him); 2018 → 55.9k, 2024 → 53.5k; active stars (Daicos 7115,
Bontempelli 3139) untouched. 1855/2649 retired_now. `retired_now` also flows into the FLAT sheet and the
cohort-trajectory Current column; per-year trajectory sums are clean (Vpath has no floors).

Both fixes are rendering-only via `/tmp/s4_render.py` (+ `/tmp/s4_merge_retired.py` to attach `retired_now`
from static flags — no WF recompute). Engine UNCHANGED e0ac9c377d1e, Stage-0, nothing baked, no curve.

## 6. STRUCTURAL BUG — season indexing was by GAMES-PLAYED, not calendar-since-draft (FIXED, re-indexed)
Luke caught this in the eyeball. The matrix indexed each player's seasons by SEASONS PLAYED
(`if x['games']>=1`), so a player who SAT OUT his draft year 1 had his first PLAYED season relabelled "Yr1"
and his whole trajectory shifted forward a slot — corrupting both the cohort trajectories (misaligned
sat-out vs straight-through players → a spurious uniform recent-year drop) AND the CURVE ANCHOR.

CAUSE CONFIRMED (Campbell pk62 / D.Jones pk21, both draft 2022, both sat out 2023): their book "Yr1" was
their first played season (2024), not their no-games 2023.

FIX: re-index by **calendar-year-since-draft** (Yr_k = draft_year+k whether or not played; missed year =
real WF value = pedigree pole / staleness, NOT collapsed). Anchor = ASOF[draft_year+1]. Active players run
through 2026; retired stop at last played year (no post-career floor). RE-INDEX over the SAME WF as-of
values (the loop computed every calendar year already) — confirmed mapping-only: played-season values are
identical, just shifted to their correct calendar slots. Re-ran the matrix (deterministic, same values) +
re-rendered. Spurious recent-year drop resolved (last tenure-year now aligns with Current: 2018
Yr8=87%=Current, 2024 Yr2=80%=Current).

CURVE-ANCHOR BIAS — finding CORRECTS the hypothesis (BIDIRECTIONAL, net opposite): 608/2090 (29%) of
curve-eligible ND+RD sat out Yr1. Relay expected uniform OVER-valuation (first-played > no-games Yr1).
Reality: the no-games calendar-Yr1 anchor = the pedigree POLE (median ~1.42× draftval — "unproven prospect
still has draft capital", which the relay named "pedigree floor" but assumed was lower) vs the first PLAYED
season:
- 473/608 RAISED by the fix (deep picks / weak partial debuts: pole > weak first season).
- 134/608 LOWERED — exactly the relay's flagged case: high picks who sat out then debuted STRONGLY
  (O'Meara pk1 −1111, Petracca pk2 −776, Jagga Smith pk3 −1117, D.Jones pk21 −311). Those WERE over-valued;
  the fix brings them down to their unproven Yr1 pole.
- Net pool-wide anchor sum 1,237k → 1,436k (+16%).
The bug mis-anchored in BOTH directions; the curve was not uniformly over-valued. (Open question for the
curve step / supervisor: is the unproven pedigree pole the right Yr1 anchor for a sat-out pick? It matches
the relay's stated definition — flagging the direction so it's a conscious choice.) Matrix builder
`/tmp/s4_matrix.py` rewritten for calendar indexing; played-indexed backup at `/tmp/s4_matrix.played_indexed.bak`.

## 7. NO-GAMES POLE — DIAGNOSED (mechanism, not reassurance) + KAKO data fix
KAKO (ND pk13 2024): source DB was missing his 2025 debut (23g, 55.1 — Rising Star); only had 2026 (6g,
55.0), so he read as sat-out 2025 → no-games pole (~1382). FIX (scoped, in `/tmp/s4_matrix.py`, Luke
confirmed isolated): injected {2025,23,55.1}. Yr1 anchor now 1865 (played ~55 debut). sat-out 608→607.
NB source DB should also be corrected (data-reconciliation item) — the book patch is builder-local.

NO-GAMES POLE DIAGNOSIS (607/2090 = 29% of curve pool anchor on it):
MECHANISM (corrects earlier "pole" wording): a no-games player's value = `price6` (band's distribution-
weighted price given pedigree + zero production). The pole is GATED OUT — `expgate = exposure/POLE_RAMP = 0`
at zero exposure (raw_ev line 74), so `w=0`, value=`pr`. WQ6 weighting = [0.18×5, 0.10].
(a) INCONSISTENT MULTIPLE — mostly a DEAD-YARDSTICK artifact: multiple drifts (top ~0.87× → deep ~1.56×)
    because (1) OLD PVC over-decays at the deep end (PVC[70]=308) while no-games flattens to a sane floor
    (~520-700 abs) → ratio inflates deep; (2) PVC is position-BLIND but no-games is position-AWARE (KEY_FWD
    ~0.5× vs MID ~1.0× same pick — key positions score fewer pts). Both resolve with the new curve +
    position-standardisation. ONE real minor defect: pick-to-pick JITTER (MID pk3 2090 < pk5 2119) — the
    no-games (price6-only) curve is NOT covered by the isotonic monotonicity guard (ISO fits the PLAYED synth
    curve, line 81).
(b) 1.42× RECONCILED: real pool median but DEEP-PICK-DOMINATED (271/607 deep at 1.56×). By tier: top(1-10)
    0.87×, 11-20 1.07×, 21-40 1.14×, deep(41+) 1.56×. At the top picks that matter, no-games sits BELOW draft
    value (0.87×). The "1.42×" was true-but-misleading (deep tail dragged it up).
(c) OVER-CREDIT / "grew from sitting out" — NO at the top: 0.87× = already below draft value (the mild
    negative the relay said it should be). Deep 1.56× "growth" is the over-steep OLD PVC, not an absurd
    absolute. Level broadly correct; top already docked.
(d) FLOOR-AWARE — YES, structurally: (i) WQ6 weights bust-downside (q10/q30) equally with upside, q97 down-
    weighted → not ceiling-credited; (ii) lift `pr + w·recover·(po−pr)` puts PLAYED-WELL above the no-games
    `pr`, so playing well buys down the floor and outranks sitting out (Ashcroft pk5 3568 > Smith pk3 2162) —
    structural, not luck.
VERDICT: the no-games anchor is largely SOUND; the dramatic "inconsistency" is the dead, position-blind,
over-steep PVC as a bad yardstick. Only real defect = pick-to-pick JITTER, which the curve's own loclin
smoothing over log-pick will largely absorb. PROPOSED (not patched): if desired, extend the isotonic
monotonicity guard to the no-games curve per position. NO re-levelling needed. Engine UNCHANGED e0ac9c37.
Diagnostics: `/tmp/s4_pole_diag.py`, `/tmp/s4_pole_diag2.py`.

## 8. NO-GAMES SMOOTHING + VALUE-FROM-NOT-PLAYING (diagnosed, fix proposed) + EARLY-vs-LATE
STANDING INSTRUCTION reinforced: SMOOTH+loclin+monotone over the natural axis (log-pick/age/margin) is now
DEFAULT for any such curve, applied without being asked. The PVC-ratio framing last turn dodged the real
issue — dropped it. Section 7's "0.87× top is fine" is RETRACTED — it's a tier number off the broken banded
structure and can't be judged until smoothed.

NO-GAMES ANCHOR (the egregious banding was real):
- (a) BANDS/CLIFFS CONFIRMED: raw no-games value across pick is the GBM band's STEP function — flat runs
  (22/69 adjacent pairs |Δ|<5; pk61-63 all 508) + cliffs (pk2→3 −21%, pk8→9 −15%, pk12→13 −15%) +
  non-monotone (pk3→4 +147). Monotonicity alone wouldn't fix the cliffs. FIX (built as analysis): loclin over
  log-pick + isotonic-decreasing → continuous, smooth, monotone. Chart `AFL_RL_nogames_anchor_diagnosis.png`.
- (b) VALUE-FROM-NOT-PLAYING = REAL DEFECT: on the smoothed curve, from **pk7 to pk70** the no-games Yr1
  value EXCEEDS the player's own draft (Y0) value — up to **+30%** (pk70 514 vs 396). A sat-out player gains
  value. Root cause: the band's age/tenure feature response credits the extra year (age18→19, tenure0→1)
  positively for a zero-games player, and staleness hasn't docked yet (Yr2 then CRATERS to 76-746 — staleness
  kicks in at tenure 2). So Yr1 sits in an over-credit window. Only top picks (1-6) correctly have Yr1≤draft.
- (c) DEEP FLOOR: raw tail is propped/flat (pk45-70 ~520-634, even rising); smoothing tapers it −18%, but
  the LEVEL is still above draft value (same root cause as b).
- PROPOSED FIX **(0.92× cap REJECTED by Luke as an arbitrary scalar — replaced below by the
  evidence-derived decay)**.

NO-GAMES DECAY — DERIVED FROM REALISED OUTCOMES (replaces BOTH the 0.92 cap AND the staleness crater;
show-don't-wire). Method: curve-eligible realised players (cohorts 2004-18, n=1642), binned by years-sat
(cumulative "sat ≥N"), realised = peak value over PLAYED years (0 if never played → no no-games circularity,
washout=0), aggregated DISTRIBUTION-AWARE (WQ6 quantiles, not mean). Draft-value baseline = distaware
realised over all = 1665.
  bin            n     distaware   /draft   establish%   washout%
  PLAYED yr1   760        2442     1.47x       62%          —
  sat ≥1 yr    882         881     0.53x       21%         44%
  sat ≥2 yrs   192         991     0.60x       29%          1%
  sat ≥3 yrs    57         822     0.49x       28%          —
  sat ≥4 yrs    22 (THIN)   650     0.39x       18%          —
  never-established: 390 players (realised 0) → washout floor ~0 CONFIRMED.
KEY FINDINGS (all DERIVED, honestly surfaced):
  (i) decay is NON-MONOTONE yr1→yr2 (0.53→0.60) — a REAL survivor-selection effect: sat≥1 is 44%
      washouts (cut after yr1); sat≥2 is only 1% washouts (still-listed = club keeps the project = positive
      selection). The DATA contradicts the strict-monotone assumption; surviving the cut is real positive
      evidence. Recommend honoring it: a ~0.55× FLAT PLATEAU across yr1-2 (the bump is real but small), then
      decline yr3-4 toward washout — approx monotone as plateau-then-down.
  (ii) decay is STEEPER than guessed: yr1 sitter ≈ 0.53× draft (NOT the 0.70-0.85× floated), and FAR below
      the current engine's ~1.0×.
  (iii) PICK INTERACTION (smooth over both axes): top-pick sitters retain MORE — pk1-20 0.71×, pk21-40 0.59×,
      pk41-80 0.63×. So m is pick-dependent (gentler decay for top picks); apply on the smoothed pick axis.
  (iv) THIN TAIL: sat≥3 n=57, sat≥4 n=22 — derive yr1/yr2 directly (adequate 882/192), constrain yr3-4+ to
      monotone-decay-toward-washout with smoothing/extrapolation, sample-thinning STATED.
SMILLIE (pk7) resolved as the SAME issue: current Yr1=1853 (~1.0×, TOO HIGH) → Yr2=446 (~0.25× crater, TOO
LOW). Evidence says a flat ~0.55× plateau across yr1-2 fixes BOTH directions (down from 1853 to ~0.55×, up
from the 446 crater to ~0.55-0.60×). Cap-then-crater replaced by an evidence plateau.
PROPOSED SURFACE (not wired): no-games anchor(pick,N) = realised-pick-curve(pick, smoothed log-pick) ×
decay m(pick,N), both axes smooth, washout floor, thin tail flagged. Scripts `/tmp/s4_ng_derive.py`,
`/tmp/s4_ng_derive2.py`.

FAITHFUL EARLY-vs-LATE (pk8 EARLY/Serong vs pk5 LATE/Parish, full 22g): trajectory STILL wins as the lower
pick — EARLY@Yr2 (84,pk8)=3567 vs LATE@Yr3 (80,pk5)=3403 → +5% (narrowed from +18% at equal picks; the
pedigree deficit eats most of the trajectory premium). EARLY@Yr1 (78,age19,pk8)=3148 < LATE@Yr3
(80,age21,pk5)=3403 (the more-proven higher pick wins when EARLY is only 1 season in). Early-vs-late CLOSED,
no age-axis fix. Script `/tmp/s4_el2.py`.

AGGREGATE PEAK (item 3 — OVERALL row added to Table 1, both measures): mean across curve cohorts (2004-24)
of Measure-1: Yr1 100%, Yr2 91%, Yr3 106%, Yr4 123%, **Yr5 129% (PEAK)**, Yr6 123%, Yr8 90%, Yr10 55%. So
the aggregate peak is 129%@Yr5 — at the TOP of Luke's target ~120-130%, NOT the 140-150% the per-cohort
eyeball suggested (calendar re-indexing pulled it down). Suggests the plateau/decliner decay-generosity fix
may NOT be needed at the aggregate level, though individual cohorts vary higher. `/tmp/agg_peak.json`.

## 9. TWO GATES CLEARED + POSITION-AWARE DECAY + YEAR-2 DECOMPOSED (still NOT wired)
Decay confirmed READY in principle (plateau honoured, level right ~0.53-0.60×), held behind two integrity
gates which are now BOTH CLEARED. Still NOT wired — simulation revealed a new peak interaction (below).

ITEM 2 — POSITION-AWARE DECAY (built): decay split by position group vs that group's own baseline —
  RUC  sat≥1 0.76× / sat≥2 0.97×  (sitting barely dents a ruck — slowest developers; thin at yr2, n=26)
  KPP  sat≥1 0.59× / sat≥2 0.71×
  nonKPP sat≥1 0.45× / sat≥2 0.47×  (a mid who sits usually isn't good enough)
Position effect REAL and large → decay MUST be position-aware (gentler KPP/RUC, steeper non-KPP); RUC own
(gentlest) treatment. PICK-INTERACTION re-examined WITHIN position: it SURVIVES (top-20 premium in both KPP
pk1-20 0.76 vs 0.57-0.58 deeper, nonKPP pk1-20 0.69 vs 0.47-0.50) and position MIX is stable across pick
bands (~25% KPP everywhere) → NOT position wearing a pick costume; both effects real & ~independent. But the
pick effect is a top-20 premium then ~flat, NOT a 3-tier gradient → smooth over log-pick WITHIN position.
Final surface = realised-pick-curve(pick, within position) × m(pos, pick, N), both axes smooth, plateau
yr1-2, washout floor, thin tail flagged. Script `/tmp/s4_ng_pos.py`.

ITEM 3 — POLE DOUBLE-COUNT GATE: **CLEARED (proven clean)**. (1) Engine per-year STATELESS — a sit-then-debut
player's debut value computes from scoring≤debut only; the yr1 no-games value (1514) is NOT an input to yr2.
(2) Decay = multiply on no-games years only — applying ×0.55 to the sat year drops it (1514→833) while played
years 2022/2023 stay BYTE-IDENTICAL. (3) NO recovery bonus: A (sat then debut 15g@75, tenure2) = 2330 < B
(fresh debut same production, tenure1) = 3012 — the sitter is if anything PENALISED (older, less runway).
Decay governs no-games years, pole governs played years, no boundary overlap. Script `/tmp/s4_pole_handoff.py`.

ITEM 4 — YEAR-2 TROUGH GATE: **CLEARED (decomposed; decay fixes it, doesn't deepen it)**. OVERALL Yr2=91% is
NOT a real sophomore slump — decomposed (pooled, curve cohorts): PLAYED-yr1 (1483) RISE +6% (106%, normal
development); SAT-yr1 (607) CRASH −46% (54%) from inflated ~1.0× yr1 to cratered yr2. Sat group = 28% of yr1
total but 145% of the drop. So the trough = the no-games yr1 inflation unwinding (the exact defect). SIM of
the decay on the cohort trajectory:
  before  Yr1 100  Yr2 91   Yr3 106  Yr4 123  Yr5 129
  after   Yr1 100  Yr2 110  Yr3 124  Yr4 144  Yr5 150
→ Yr2 trough LIFTS 91→110 (does NOT deepen — gate cleared). BUT PEAK RISES 129→150 (docking inflated yr1
shrinks the baseline → all later ratios lift). 150% is the TRUE peak off a CORRECTED baseline — MATCHES Luke's
140-150% eyeball. The 129% was masking the real peak behind the inflated baseline; Luke's "peak too high" read
is VALIDATED, and plateau/decliner decay-generosity is now the LIVE next item (DOWN-side, distinct from
no-games). Script `/tmp/s4_yr2.py`.

DISPOSITION: both gates clear → no-games decay is wirable (position-aware plateau + within-position pick
smoothing). But wiring ALONE pushes the peak to 150% (above Luke's 120-130% target) → recommend coordinating
no-games wiring WITH the decliner decay-generosity fix, or at least flag the peak lift. HELD for Luke's call.
Sim M-values (sketch, pre pick-within-position smoothing): KPP{1:.59,2:.71}, RUC{1:.76,2:.97}, nonKPP{1:.45,
2:.47}, yr3-4 decline toward washout.

## NEXT (after Luke's eyeball — DO NOT start until he returns the read)
Build the curve from verified anchors: distribution-aware value per ND pick smoothed/loclin over log-pick
(continuous ND→RD order), position-standardisation + ×0.95/1.0/1.05 factor; compute MSD/SSP/post-draft
pooled distribution-aware values + ND-pick equivalences (resolve the post-draft-granularity judgment call).
Fix any mispricing the eyeball surfaces BEFORE averaging. Engine stays e0ac9c377d1e, Stage-0, NOT baked.

## Key paths
Engine `rl_after/_merged_recover.py` md5 e0ac9c377d1e1a540690a346ca331d63. Matrix builder `/tmp/s4_matrix.py`
(→ `/tmp/s4_matrix.json`), renderer `/tmp/s4_render.py`. Env (every cmd): `PYTHONHASHSEED=0 RL_GAMMA=0.85
RL_PICK1=3000 RL_RUCK_TAX=0.25 RL_RECENCY_DECAY=0.72 RL_PRIOR_TREES=400 PAR_RAMPS=22` +
`PYTHONPATH=/home/claude/rl_workspace/rl_after`.
