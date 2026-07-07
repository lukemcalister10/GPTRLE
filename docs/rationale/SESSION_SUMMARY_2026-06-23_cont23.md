# SESSION SUMMARY — 2026-06-23 (cont.23): cont.22 VERIFIED + by() CRASH FIXED + ROSTER→805 + PARITY ROOT-CAUSED

## DONE & VERIFIED
1. **cont.22 work verified at source level.** Master = 2656 records, scoring from 2005, new cols
   (dob/phantom/double_count/pvc_exclude/eyr) present; DOBs folded in (Tuck `_bd`=1981-12-24); Betts/Ware/
   Thursfield → 2004 RD #1/#2/#3; Bramble 2020 SSP/91g. **Sharman = 310** on the board (302 raw value());
   the cache fix is real and correct.
2. **§9 AS-OF CONTAMINATION is RESOLVED — and PROVEN, not just asserted.** Re-ran cont.21's stress test on the
   fixed engine (snapshot @2026 → as-of loop 2015/2018/2021/2012/2009 → reset → diff): **0 of 788 values drift**
   (Sharman 302, Newcombe 1871 stable). cont.22 correctly OVERTURNED cont.21's §9 — the polarity was backwards:
   1147 was the STALE-cache artefact, ~310 is correct, and the as-of loop's `_pe_clear()` was *revealing* the
   right value. **In-process backtests are now reliable.** (peak_est is keyed `(id(p),BASE_REF)` and `_backval`
   deepcopies, so 2026 board entries are structurally protected.)
3. **by() None-guard bug FIXED (cont.22-introduced, not caught by cont.22).** `def by(p)` (rl_model.py L60) was
   `p.get('_by', p['year']-18)` — but cont.22's DOB fold-in wrote explicit `_by=None` into ~302 DOB-less records,
   and `.get(key,default)` returns the None, crashing `_age_at` (`2026 - None`) on ANY `value()` over those records.
   The shipped board was SAFE (0 of the 805 active players have null `_by`), but the **retention backtest / cohort
   analysis / walk-forward harness all crash** on the historical records. Fixed L60 → `p.get('_by') or (p['year']-18)`
   (guards None like L367 already does). With the fix the prototype runs and matches the kickoff's expected anchors
   (Willem 2702 > Uwland 2122; Sheezel 6823; 2024=92%, 2025=90%).

## ROSTER → 805 (active-17 RESOLVED)
The active pool is **805 = 788 + 17 undebuted-but-rostered players**. They all simply LACKED the `force_active`
flag, so `active()` fell through to `played and recent` (requires ≥1 game) and dropped them for 0 games. Set
`force_active=True` for the 17 in BOTH master copies + the runtime JSON. Verified 805 exactly (arithmetic: 788+17,
nothing else moved); all 17 price as sane prospects (Will Green RUC#16 830, Ollie Murphy KDEF#41 413, pickless
IRE/UNR/PDN ~238-291, Brayden George 2022-undebuted 161 — no-evidence decay correctly biting).
**The 17:** harry-demattia, ollie-murphy, will-green, xavier-walsh, reece-torrent(2023 ND#64), oscar-ryan,
brayden-george, zak-evans, matt-duffy, matt-hill, caleb-lewis, cillian-burke, rob-monahan, ryda-luke,
riley-hamilton, benny-barrett, jacob-moss.
**GROUND-TRUTH RULE (Luke, locked):** 805 is the manually-maintained active list. Luke personally informs of
delistings/draftees. No mechanism should auto-decide a rostered player inactive. `force_active` is the manual
roster flag (now 63 set). Belt-and-braces QoL (retire the `played and recent` heuristic for a pure allowlist) is
DEFERRED — not worth disrupting now; the failure mode that mattered (undebuted rookies) is covered.

## DIAGNOSED, PARKED — JS PARITY (~189/788; HTML is DO-NOT-SHIP)
Root cause = the **un-ported out_tilt cut from cont.21**, NOT cont.22's data changes. Verified: out_tilt is CUT in
Python (rl_model.py L656) but still COMPUTED + APPLIED in JS (`_engine_block_v23.js` L33 def, L79
`relative=clamp(relC(...)*outTilt(p,gf,ep),...)`). cont.22's DOB/cache changes flow BAKED into the JS
(`p.pn`/`p.age`/`p.ln`, L78) so they auto-match Python and CANNOT cause a parity gap. The gap lands on young/
high-pedigree players because that's who out_tilt swung (±300-470; Curtin gap ≈ +470). **The handover's
"parity gate 0/785" was STALE** (from cont.14, never re-verified after cont.21's out_tilt cut) — cont.22
mis-attributed its own "regression" to its data work.
**FIX (parked):** remove `* outTilt(p,gf,ep)` from `_engine_block_v23.js` L79, rebuild, re-verify parity (don't
assume one line zeroes it — re-run the gate). PARKED to batch with the U21-1 floor-wire JS port (same `relative`
line) per Luke's one-rebuild-per-session discipline.

## DECISIONS THIS SESSION
- **NEXT BUILD: U21-2 first-order walk-forward harness** (in progress). Resolves β honestly across ~10-12 clean
  cohorts instead of locking on 2 (2024/25, both right on the 90% floor); verifies the in-sample-leakage
  hypothesis (currently asserted); becomes the calibration backbone for the floor work (U21-1, U19-4, U21-4).
- Board ship PARKED (out_tilt JS port batches with the floor-wire).
- Torrent confirmed **2023 ND #64** (data already correct).

## U21-2 WALK-FORWARD HARNESS — BUILT & RUN (forward_valuation/walk_forward_harness.py)
First-order: retrain v4 per test year with a genuine TARGET-WINDOW CAP (cap=D+1, cohort D held out),
X built with the engine's own `_v4_feats`/`_v4_draft_feat` (train==predict features), swap `MA._V4MODEL`,
aggregates fixed. Run: `cd rl_after && PYTHONHASHSEED=0 python3 ../forward_valuation/walk_forward_harness.py`.
**RESULTS (14 cohorts 2012-2025):**
- **Harness sanity PASSED:** already-clean 2024/25 walk-forward (91/93%) ≈ in-sample (94/94%) — no spurious shift.
- **LEAKAGE HYPOTHESIS CONFIRMED (was asserted):** value() in-sample mean 106% → walk-forward 96% (9-pt hindsight);
  drop scales with cohort age (2012-14 fall -15..-18, exactly the memorised-career signature).
- **β CALIBRATION (new_value floor, walk-forward = honest):** β=0.80 mean 93%/min 88% (2024,2025 breach);
  **β=0.85 mean 96%/min 90% (2025 exactly on the line)**; β=0.90 mean 98%/min 92% (none breach, but hot vs the
  ~95% avg target + props unproven picks more). 2024/25 (newest) are the binding constraint at every β.
- **RECOMMENDATION (awaiting Luke):** 0.85 is now genuinely lockable (14 cohorts, not 2) and matches the
  ~95%-avg/≥90%-floor guideline, but is marginal on the cohorts Luke drafts into. **β≈0.87 interpolates to ~91%
  on 2025** with mean ~96-97% — the comfortable middle. Final β is Luke's call (speculative-floor tradeoff,
  interim until U21-4 distribution pricing replaces β).
- The harness is now the CALIBRATION BACKBONE for U21-1 floor-wire, U19-4 position tilt, U21-4 distribution.

## METRIC NOTE (cont.23) — what year-1 retention does/doesn't measure
Year-1 cohort retention is a FLOOR-CALIBRATION metric (does a fresh cohort price near draft expectation?),
NOT a cohort-strength metric. It is pedigree-floor-dominated and structurally blind to future busts — at debut
nobody has busted yet. Proof: the 2020 class is the weakest mature cohort in REALISED terms (48% bust, only
Holmes/Gulden before a cliff; realised-retention proxy ~29% vs 64-81% for 2017-19) yet reads a healthy 93%
year-1 because the busts only get written down in years 2-4 (production signal + no-evidence decay). This is the
harness working as intended (pricing 2020 low at year-1 would require the exact hindsight the walk-forward strips).
For COHORT-STRENGTH validation use year-3/year-4 retention (2020 should fall hard) — easy to add as a standing
check; do NOT misread a healthy year-1 number as "good cohort."

## β DECISION (cont.23) — AGREED & READY TO WIRE: β=0.85 + global-clock season-proportional phase-in
- **β=0.85** — Luke's lean, validated lockable on 14 cohorts. AGREED as the working value (final-lock at wire time).
- **Season-proportional phase-in (AGREED, folds into U21-1 floor wire):** β=0.85 is the END-OF-SEASON floor level
  and PHASES IN PROPORTIONALLY to season progress, CONTINUOUSLY — not switching on fully at draft/debut, not
  stepping at season boundaries. Applies to ALL tenure years the floor affects (interpolate between season-end
  anchors by the season fraction), not just year-1.
- **CLOCK = GLOBAL COMPETITION ROUND COUNT (CONFIRMED), not personal games.** Same fraction for everyone (R15/24 ≈
  60% now). A player who debuts later is NOT advantaged — Luke: if they're not good enough to get an early game
  while another player is, that shouldn't be a valuation edge. So phase-in tracks rounds-elapsed/total, identical
  for all players regardless of when/if they've debuted.
- Does NOT disturb the β calibration (retention measured as-of season-END, fraction=1.0). Only moves the LIVE
  mid-season board (+ fwd/back boards at their season points). Hook: `_season_games()` (rl_model.py L180-182).
  Implementation: continuous clock `seasons_eff = (AGE_REF - debut) + season_frac`, decay schedule anchored at
  integer season-ends. Promoted from "optional polish" to a REQUIREMENT (the live board is mid-season now).

## PRE-FLOOR-WIRE REVIEW CHECKPOINT (cont.23) — Luke reviewing before U21-1
Luke asked to see a full cohort backtest BEFORE the floor wire moves the board. Regenerated
`master_backtest.py` on the CURRENT engine (cont.22 fixes + 805 + by()-guard) →
`AFL_cohort_backtest_MASTER_2003-2025.xlsx` (Summary + per-cohort 2003-2025, per-player draft→peak→year-by-year,
cohort totals as live SUM formulas, 0/3001 formula errors). **KEY VALIDATION:** the Summary career-year ratios
confirm the engine writes weak cohorts down over time — 2020 runs 0.96→0.94→0.73→0.65→0.66→0.54 (Yr1→Yr6),
visibly the worst decliner, exactly matching Luke's "2020 was weak" read and the metric discussion (year-1 is
floor-calibration; strength shows in years 3-6). This is the ground-truth baseline to eyeball before the floor.
**MATURE-AGE CANDIDATES (U21-3):** added `MatureAge_Candidates` tab — 52 Bramble-shaped (entry>=2023, age@draft>=22)
with scoring spans + a verdict column. GAP-flagged (highest suspicion): **Flynn Perez** (2025 SSP, scoring back to
2020!), **Lachlan McAndrew** (2024 SSP, 2023 scoring; the ~1755 anchor), **Jack Buller** (2023 MSD). Caveat:
McAndrew/Perez are documented auto-recalls so the gap may be the re-entry convention, not corrupt data — confirm.
**Blakiston is CLEAN** (2025 entry, 2025-26 scoring, no gap — genuine recent mature rookie, NOT a Bramble; Luke's read).
AWAITING Luke's eyeball on the backtest + the mature-age verdicts, THEN the floor wire (U21-1).

## FLOOR PREVIEW — current vs β=0.85, all 805 players (cont.23) — BREAKAGE SCAN before wiring
`AFL_floor_preview_current_vs_b085_2026.xlsx` (Board / Movers / Cohort summary / Position summary; 0/3274 errors).
Computed bal-level MA.value vs new_value(0.85) at 2026 for every active player (cvx is a separate unchanged
multiplier on top, equal both sides). **No breakage found:**
- **Aggregate board +0.2%** (value-neutral, as β-calibrated).
- **All proven anchors UNCHANGED** (Sheezel/Daicos/McAndrew/Sharman/Thilthorpe +0) — floor only touches young/unproven.
- **Fallers = inversion fixes working:** Uwland −35%, Harry Dean −36%, Willem −15%, and the ORDERING is now correct
  (Willem 2702 > Uwland 2122 > Harry Dean 1959; old pedestal had Uwland above Willem).
- **Mature-agers correctly de-propped** by the runway gate: Bice −54%, Mannagh −39% (no rookie option floor at 29yo).
- **Risers = the speculation premium (the judgment zone Luke should eyeball):** Jhye Clark +96% (409→800), Zane
  Duursma +38%, Sid Draper +11% — slow-starting high picks propped toward β·PVC. None absurd (max lands ~800).
  Whether 0.85 is too generous to slow-starting top picks is the live call; distribution pricing (U21-4) refines it later.
AWAITING Luke's eyeball on the 805 before the wire. (NOTE: this is bal-level to isolate the floor; the per-year
floor-applied historical backtest is a heavier build — harness already validated cohort retention under this floor.)

## ⚠️ PLAN CHANGE (cont.23) — DO NOT WIRE THE FLAT FLOOR ALONE; DISTRIBUTION PRICING (U21-4) PULLED TO #1
Luke's per-player audit of the floor preview rejected wiring the flat β·PVC floor in isolation. It fixes the
inversions but BAKES IN two failures (one root cause: point-estimate + flat pedigree prop, no variance/trajectory):
(a) ceilings compressed — Willem (pick-1 MID, 86.4 as an 18yo) projects only 101.6; the "elite debut + top pedigree
→ star" signal lives in the upside tail a mean discards; (b) floors prop the stalled UNIFORMLY — Clark (pick-8 MID
at 41 = HALF replacement, yr3) floored at 800, Zane (pick-4) at 1372; the floor decays by seasons, never by HOW FAR
from the mark; (c) not-playing protects pedigree (Patterson/Annable) while playing-well caps you. Mature-age over-cut
(Mannagh→305 via runway gate) + recency under-weight (Bice: improving form projected below current) compound it.
**LUKE'S ORGANISING INSIGHT:** pedigree = PRIOR; performance updates it IN PROPORTION TO THE MAGNITUDE of the gap
(confirm→holds high, contradict-by-a-lot→collapses but keeps a residual floor, small miss→moves a little). Value =
E[v(outcome)] over that distribution on the convex scale → young-gun premium AND staller discount from ONE quantity.
**DECISION: build distribution pricing WHOLE (no patch), it replaces β·PVC floor + cvx + runway + tenure decay.**
Full proposal in `DISTRIBUTION_PRICING_SPEC.md` (quantile models for the conditional distribution, pedigree-prior
blend for sparse top-of-draft, double-count recenter, harness-calibrated to ≥90% retention). AWAITING Luke's
feedback on the spec before building. The U21-1 flat-floor wire is SUPERSEDED by this (the inversion fix comes for
free inside the distribution). out_tilt JS port + 805 + by()-guard still ship with whatever board build comes next.

## STAGED, NOT BUILT
by() guard (L60) + force_active 805 (master both copies + JSON). **HTML board NOT rebuilt** — still shows 788 and
pre-out_tilt-port. Backups: `rl_model_data.json.bak_pre_active17`, `afl_master_db.xlsx.bak_pre_active17`
(rl_after + rl_build).
