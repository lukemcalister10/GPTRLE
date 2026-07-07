# DIRECTIVE 3 notes — 2026-07-02 — board layers + A2 residual + drop-fix design + B4 isolation
_Head `8aed420a` store `644d1254` band `34faa865` — all unchanged; scratch evaluations only; gate-script/doc
edits per STEP 0. Post-merge main = `fc81493` (PR #5 merged this session). Restore-verify 9/9 + panel 10/10._

## STEP 0 (all landed)
- PR #5 merged → main `fc8149361b709693997c5feac891de8599d75b5c`.
- **A2 AMENDED** in `ship_gates_check.py` (Luke, in writing, 02/07, verbatim reason in CHANGELOG): Curtis leg
  Ward<Curtis → **Curtis ≥ 0.90×Ward**; Weddle leg + A9 unchanged. At-head ratio 0.652 → still red; under the
  M1+v7 overlay 0.868 (D2) / 0.873 (this session's reconstruction) → still (barely) red.
- **B2 tol = 0.5 %-pts** set (supervisor ruling under delegation; N=5 spread 0.00). GATE-1 re-run this
  container: leakage 0.0 → **B2 PASS at the new tolerance**.
- B5 denominator-versioning CHANGELOG line recorded; SHIP_GATES.md untouched (`764a0d91` preserved).
- Permanent session rules (i)–(iv) registered in START_HERE.md §6 + docs/KICKOFF_PROMPT.md.
- Full gate board re-run at head post-amendment: **statuses unchanged** (9 FAIL / 8 PASS / 5 PENDING /
  1 STRUCK — B2 flipped NOT-RUN→PASS; report `ship_gates_report_8aed420a.md` regenerated).

## ASK 1 — board layers (full pack: `board_layers_pack_D3.md`; JSON: `scripts/d3_ask1_board_out.json`)
1a: gates price [ENG] `_merged_recover.ev()`; the [BOARD] export path (`rl_export.py` → `rl_model.py` +
`wire_redesign` → `TR.production_value`; JS shows `v` verbatim, legacy chain dead at `_engine_block_v23.js:97`)
never supplies a gate number except B4's byte-compare.
1b: eight live layers + one inert + a dead JS chain enumerated with toggle-off repricing (wire overwrite
31.6% of board value; REPL−3 19.6%; tail-restore 1.4%; RUC pool 1.1%; RUCK_TAX 0.3% — **LIVE on the board,
DEAD only on the engine path; the ledger conflated the paths**; soft floor 0.1%; Brodie exactly 1 player;
lens tilt inert at 'bal').
1c: dual-path ruler — **A4, A9, A11 flip PASS↔FAIL between paths**; A10 0.51 vs 0.68; B5 9 vs 18 offenders;
aggregate: board −7.6% total, median player |Δ| 24.9%, 57% differ >20%, Spearman 0.903.
1d: CONFIRMED — 2866 = Rozee-under-proration, decay-proration report line 17 (2679→2866).
1e: shipped bundle `b8f9e998` = pre-2026-06-21 export-code generation (PVC[1]=3883 predates the RL_PICK1
anchor) + older store (785 active, cohort 1303) — an orphaned artifact; see ASK 4.

## ASK 2 — A2 residual (Curtis 1087 < Ward 1253 under the overlay), one factor at a time
Baseline (at-head) decomposition, `ev(p,Y)` gate-method, channel a = drop the 2026 row then advance the year,
channel b = the 2026 row's level pull:

| player | g26 | ev25 | ev26 | ch a (decay+age) | ch b (2026 level) | exposure 25→26 |
|---|---|---|---|---|---|---|
| Connor Rozee | 2 | 3874 | 2679 | −827 (−21.3%) | −368 (−9.5%) | 70.5→52.8 |
| Josh Ward | 13 | 2290 | 1782 | −641 (−28.0%) | **+133 (+5.8%)** | 47.2→47.0 |
| Paul Curtis | 13 | 1315 | 1162 | −303 (−23.0%) | **+150 (+11.4%)** | 52.0→50.5 |
| Joshua Weddle | 12 | 1887 | 1628 | −297 (−15.7%) | +38 (+2.0%) | 44.8→44.3 |
| Jack Ginnivan | 13 | 1432 | 1578 | −319 (−22.3%) | **+465 (+32.5%)** | 58.7→55.3 |

**2a / h-CurtisDrop: FALSIFIED.** All four A2 players are ON-PACE (12–13 games of 2026); their thin-season
channel is POSITIVE and their decay/exposure-alone share (3a split) is Curtis **+0.5%**, Ward −6.2%,
Weddle −3.8%, Ginnivan −1.6%. The A2 residual is NOT contaminated by the current-season drop, and the scoped
drop fix verifiably moves none of them (+0.0%). Its fix does NOT ride the drop fix.

**2b Curtis full stack:** ev25 1315 → age/tenure −310 → decay/exp +7 → no-26-row 1012 → 2026-level +150 →
head 1162 → overlay: M1-only LIFTS him (1441), v7-only CUTS him (977), combined 1156. The thing holding
Curtis down is the v7 band compression, not the calendar. Post-overlay vs pick-and-age-matched genuine
producers (nq≥3, level ≥0.9×par, nearest log-pick+age):

| target | overlay value | matched five (overlay values) | matched median | sits at |
|---|---|---|---|---|
| Paul Curtis | 1156 | Soligo 2243 · Roberts 1521 · Owens 1741 · Hough 241 · Neale 2103 | 1741 | **66%** |
| Josh Ward | 1324 | Amiss 912 · Rachele 1711 · Andrew 3367 · Humphrey 1305 · Wanganeen-Milera 5770 | 1711 | **77%** |

Both sit BELOW their matched lines (Curtis lower). Neither the drop (2a) nor the overlay reproduction gap
explains Curtis-vs-Ward. **Proposed next isolation (not run):** per-term v7 ablation (cB-only vs asc-only)
across Curtis + the matched five, alongside a GEN_FWD-vs-MID replacement/pole axis check — decides whether
the residual is v7's evidence/age schedule or position replacement.

**Overlay reproduction caveat:** D2's Task A scratch was not committed; the s4-faithful reconstruction gives
Ward 1324 / Curtis 1156 / Weddle 1401 / Ginnivan 1675 vs D2's 1253/1087/1414/1677 — relativities and every
gate status identical (Curtis/Ward 0.873 vs 0.868), absolute values ±5%. Flagged, not silently reconciled.
This session's harnesses are all committed.

## ASK 3 — drop-fix design (design doc: `dropfix_design_M2exposure.md`; nothing wired)
3a split bundle: channel a is age/tenure-dominated (young −40.1% age vs −12.9% exposure; old −26.1% vs
−0.6%; Rozee −17.9% vs −3.7%). 3b lever: prorated exposure clock, f=0.545 derived (robustness band
0.52–0.68, A3 flat across it), evidence-replacement scope s=clip(1−g_Y/11,0,1), byte-exact at f=1.
3c: 9→10g seam EXCLUDED (assigned to cliff-blend as seam #2; `_eo` keys on raw games — orthogonal, B6
byte-identical under fix; cliff-blend `ns==0` branch reads no exposure — compatible in either order).
3d results: on-pace collateral **ZERO** (0/288 >2%, max 0.00%) · historical inertness byte-exact · B-gates
hold (B1 spliced PASS peak N4 R160 17/17; B5 9→8; B6 identical) · **A3 0.692→0.706 FAIL vs 0.80** ·
**A10 0.511→0.511 FAIL vs 0.70** (Curnow on-pace, 13g — DATA-CAUSED candidate under the [DC] triage) ·
M1+v7 interaction: overlay A3 0.642→0.659 — the fix does NOT repair the compounding. The acceptance is
unreachable through the decay/exposure channel alone; residual owners quantified in the design doc
(age/tenure sibling lever = Luke decision; A10 = data-real candidate).
**D1 attribution corrected:** the unscoped exposure-only prototype reproduced the on-pace collateral
(86/288 >2%, James Jordon −21.5% again) with `_lvl_wt` untouched — D1's collateral was the band's
non-monotone exposure-feature response, not `_lvl_wt` perturbation.

## TASK Q
- **Q1:** CONFIRMED designed behavior, with one flag — Ward: M1 fires on the 2025 basis (Lc−Lo=5.9 ≥ TOL 5,
  recent-adequate true → +6.7) and stops firing on the 2026 basis (Lc−Lo=3.0 < 5) while v7 tightens
  (cB .387→.470, asc .76→.67) → −30%; Ginnivan: M1 fires on BOTH bases and his 13g/high-avg 2026 lifts his
  current level → +6.3%. Flag: Ward's flip is a TOL_M1 knife-edge (5.9→3.0 across one basis change).
- **Q2:** `nq` = qualifying-season count (`_nqual(p, 2026)`): seasons with ≥10 games, counted from DEBUT
  (rows after the draft year; debut year = draft year+1, MSD = draft year), through the in-progress 2026
  inclusive once it reaches 10 games; a <10-game season (including a not-yet-10-game 2026) counts zero.
  Verified against the pack: Ward 5, Rozee 7, Bontempelli 13.
- **Q3 (neutral, exact):** `draftval(p) = PVC[min(effective_pick, KMAX)]`, computed at RUNTIME by the
  CURRENT head on every load — PVC is the realized-value CE pick curve (`build_pvc_v34` from matured
  cohorts), height-scaled, then whole-board anchored so PVC[1] = RL_PICK1 = 3000 (Luke, 2026-06-21), then
  de-plateaued. It is NOT computed once at draft time — it is retrospective and moves with every head/store.
  It is neither a pure intake prior nor a fixed RL_PICK1 curve: an empirical realized-value curve wearing an
  RL_PICK1 anchor. The planned PVC stage REPLACES this curve, so draftval re-bases automatically → the B5
  denominator versioning question follows Q3's answer exactly as logged.
- **Q4:** MSD/SSP (and RD) entrants receive a mechanism pick-EQUIVALENT effective pick (MSD→59, SSP→94,
  RD pick 3→61 among the nine) — it feeds BOTH live board values (band pedigree feature, par prior, pole,
  iso guard) AND the B5 denominator (draftval = PVC[equivalent] = 308): one shared object. Nine-offender
  table in `board_layers_pack_D3.md`.
- **Q5:** store 2654 valid-position rows → 805 non-retired = 805 LISTED (= the board count) → −84 pickless
  → 721 with draftval → −18 drafted-2026 → 703 tracked years 1–12+; D2's 696 = the same chain minus 7 rows
  at the yr12+ pooling boundary (exact D2 trim not recoverable from its notes). **Board 805 vs league ~805:
  NO coverage gap.**

## TASK G3-CLEAN (proposal only — tables in `board_layers_pack_D3.md`)
ND-only yr1 p5 = **0.50** vs contaminated 0.16; the yr1-below-yr2 anomaly DISAPPEARS (contamination test
positive — it was the MSD/SSP cohort's dv=308 denominators). Guard-shape skeleton presented with empirical
tracks for Luke to name numbers; 0.25× flat stays provisional.

## ASK 4 — B4 archaeology (table in `board_layers_pack_D3.md`; raw: `scripts/b4cuts/summary.jsonl`)
Canonical `e0ac9c37` engine × {reconciled, pre_stage0, stage0}: `1898ead7` / `1898ead7` / `c16e1024` —
NONE reproduce shipped `b8f9e998`. Store axis moves SCALE by 0.00051; `_merged_recover` axis provably off
the export dependency graph (no import anywhere on the export chain — grep-verified, and the swap changed
nothing). New dating fingerprint: shipped PVC[1]=3883 vs the RL_PICK1=3000 anchor (code-dated 2026-06-21)
+ active 785 + cohort 1303 → the shipped board's export CODE+STORE generation predates the anchor. Cause
stays UNLABELED (nothing reproduced); h3 strengthened; the reproducing state is not in git. Next isolation
candidate: only if a pre-06-21 export-code backup exists outside git (Luke's tarballs) — otherwise the
artifact is orphaned and the ONE-price ruling (1c) decides what replaces it.

## Hypothesis register after D3
- **h-CurtisDrop** (Curtis's A2 lowness partly the calendar artifact): **FALSIFIED** (drop-channel ≈ 0;
  scoped fix moves him +0.0%).
- **H-WARD**: stays FALSIFIED-as-sole-cause; the residual is now localised to v7's compression vs matched
  producers (Curtis 66% / Ward 77% of matched lines); next isolation proposed, not run.
- **B4-h1**: stays NOT CONFIRMED; **h3 strengthened** (export-code-generation fingerprints; store axis
  moves 5th decimal only; engine axis provably inert).
- **H1 (`_lvl_wt`)**: stays FALSIFIED; D1's on-pace-collateral attribution CORRECTED to the band's
  exposure-feature response (reproduced with `_lvl_wt` untouched).
- **NEW (from 3a, decomposed not labeled):** channel a is age/tenure-axis dominated in every cohort;
  the decay/exposure share is young-concentrated and small.

## What did NOT move
Engine `8aed420a`, store `644d1254` (+ `.pre_stage0`, `.stage0` untouched), band `34faa865`
(cm cache byte-identical, pinned across all B4 cuts), SHIP_GATES.md text (`764a0d91`), panel expectations,
five-state statuses, gate board statuses at head (9F/8P/5PEND/1STRUCK; B2 NOT-RUN→PASS is the only status
change, from running GATE-1 under the new tolerance). All workspace swaps restored and md5-verified in-run.
