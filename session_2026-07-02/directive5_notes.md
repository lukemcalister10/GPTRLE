# DIRECTIVE 5 — session notes — growth-law gate rebuild + per-term decomposition + B5 evidence + LTI register
_2026-07-02 · BUILD · branch `claude/growth-law-gate-rebuild-byxfog` · post-merge main `cecb0cc1` (PR #7 merged as STEP 0)._
_State: canonical head `8aed420a` / store `644d1254` / band `34faa865` UNTOUCHED except Luke-ruled gate/doc changes (SHIP_GATES.md B1 amendment `a55921f6`, ship_gates_check.py `5e6e34d9`, LTI register `1b24df4e`) · CANDIDATE `fb39d88a` measured READ-ONLY, zero commits to it · restore-verify 9/9 + panel 10/10 at session start; canonical workspace files restored + md5-verified after every candidate/variant swap._

## ASK 1 — NEW-B1 GATE REBUILD (PASS; Luke's redefinition wired + measured)
- SHIP_GATES.md B1 amended (Luke-ruled, in writing, confirmed; CHANGELOG quotes the ruling verbatim per the amendment process): the gate now tests the CROSS-COHORT UNWEIGHTED AVERAGE of indexed cohort value at each year-depth (rise from yr1 to a peak in yrs 4-6; pre-peak dips of the AVERAGE <5% tolerated — tolerance carried from old B1, average-only now). Per-cohort curves UNGATED but printed as a pipe table on EVERY gates-board run (stdout + report — Luke's eyeball channel). The pooled test AND the per-cohort backstop both retired; the backstop got an obituary-style CHANGELOG note (what/why/ruling ref).
- Measured at three states (`d5_ask1_newB1_three_states.md`, matrix-only — B1 never loads the engine): head 8aed420a **PASS** (avg row 100/132/146/**161**/158/148/131, peak N=4, path_ok) · candidate fb39d88a **PASS** (100/130/138/**148**/142/134/119, peak N=4) · same-builder fix-off control **PASS** (=head numbers). 2020 row explicitly: head/control 100/112/118/109/110/110 · candidate 100/111/110/**97/98/95** — visible, UNGATED. **THE D4 B1 BAKE-BLOCKER DISSOLVES under the redefined law.**
- Full rescripted board re-run at head: 9P/8F/5PENDING/1STRUCK (unchanged counts; B1 PASS in new form; B2 PASS on fresh gate1 rerun, leakage 0.0).

## ASK 2 — M1+v7 PER-TERM DECOMPOSITION (PASS; the bake-deciding channel decomposed)
- Terms + toggles (anchored one-line patches on the candidate engine, variants md5 `34343293`/`ca9df823`/`442b92a3`): **M1** (level up-branch lift) · **v7-cB** (upper-quantile band compression) · **v7-asc** (age-scaled q97 tail) · M2 context toggle via RL_EXPO_F=1. 5 measurement loads + 3 same-builder (7147) matrix builds + gate1, ALL SEQUENTIAL.
- Term table (`d5_ask2_term_table.md`; doc `d5_ask2_perterm_decomposition.md`): **(a) the Curtis compression is v7-cB** (Curtis −195/−14.4%; Ward −324/−19.6%; M1 gives Curtis +184 while Ward's +3.0 gap < TOL earns 0 — the A2 ratio motion is Ward-side). **M1 owns the WHOLE A3 cost** (−0.034: M1-off restores 0.692 = head; v7 ~nil on A3). **v7-asc owns the B5 blowout** (asc-off 53 ≈ head 51; candidate 82).
- **(b) The 2020 markdown is TWO channels** (candidate vs term-off matrices, concentration = the discriminating test): **v7-asc = mediocrity-concentrated** (top-quartile −5.0% / bottom-half −33.6%, Spearman +0.706 p=1e-08 — the engine agreeing with Luke's shocking-draft read; Gulden −1.4%) · **v7-cB = INDISCRIMINATE** (ρ=−0.024 p=0.87 — no value-rank structure; artifact-shaped) · M1 LIFTS the cohort +3.9%. Either compression term off restores 2020 above 100 at d4-6 (105/106/10x); the dip needs both stacked. Whole-overlay: −11.6%, ρ=+0.527 (`d5_ask2_2020_concentration.md`).
- New-B1 PASSES at every term state (peaks N=4: 147.6/145.2/156.6/154.3 vs control 160.5) — the overlay ruling is free of B1 blockage.

## ASK 3 — B5 EVIDENCE PACKAGE (PASS; derive + show, wired NOTHING)
- 3a (`d5_ask3_b5_offenders.md`): FULL 51-offender table at head, all columns (player/club/yrs/type/value/draftval/ratio/floor/margin), split **23 dev-window (yrs 1-8)** / **28 deep tail (yrs 9+)** — note the directive's "yr8+ tail" label: the data's actual split is yr8's 5 offenders inside the 23-bucket (as in D4), tail = yr9-18.
- 3b: the **31 joiners** at the candidate (82−51; ZERO leavers) with per-term attribution from the ASK-2 offender sets: **v7-asc solo rescues 20, +6 with cB, +1 with M2 (27/31 implicated); 4 joint**. M1 attributes zero.
- 3c (`d5_ask3c_tail_floors.md`): yr8+ floors under Luke's generating rule (0.9 × kernel-smoothed clean p5, ND-only, bw widened per depth until eff-n ≥ 35 — rule stated; 11+ POOLED deliberately, n=120, composition flagged): **d8 .011 · d9 .012 · d10 .021 · d11+ .012** vs flat **.05** and raw clean p5 .012/.013/.090/.014. The .05-forever tail binds ~4× above its generating data. NUMBERS ONLY — schedule amendment waits for Luke's word.

## ASK 4 — LTI REGISTER (PASS; verbatim commit)
`LTI_REGISTER_2026-07-02.md` md5 `1b24df4e`: the supervisor payload committed EXACTLY (D4 skeleton replaced; compatible D4 guards retained as a marked trailer). **Section A = 32 · Section B = 11** · spots: Nic Martin / Maxwell King / Connor Rozee (collision guard carried in-file).

## ASK 5 — D4 CLARIFICATIONS (PASS; `d5_ask5_clarifications.md`)
(i) **Tsatas NET candidate ev() = 979** (supervisor's ~982 was rounding; the +9.0 M1 level-lift nets to **−104** in value space, 1083→979 — BELOW Luke's "1083 OK, preferred lower"). (ii) A8 at candidate: **Berry 2197 · Tsatas 979 · 2.24×**. (iii) 6 unscored lines: A13/A14 (PVC-staged PENDING), A15 (STRUCK, stays struck), B3 (book gates unenumerated), C1/C2 (baseline books unbuilt). (iv) **Obituary = 9 layers, NOT the expected 8** — the 8 deleted layers (router incl.) + row 9 = the JS legacy chain, DEAD but bake-gated for excision; full name+magnitude column reproduced in the file.

## Hypothesis register (D5)
- h-2020-markdown-is-mediocrity-mechanism: **CONFIRMED for the v7-asc channel** (ρ=+0.706, monotone concentration down the value order) · **REFUTED for the v7-cB channel** (ρ≈0, indiscriminate — artifact-shaped). Luke's shocking-draft read holds on the asc half.
- h-Curtis-squeeze-is-v7-compression (D3's localisation): **CONFIRMED + SHARPENED to v7-cB specifically** (−195; asc −91; M1 +184 counteracts).
- h-overlay-costs-A3-0.05 (D4): **SHARPENED — it is M1's −0.034 (+M2 +0.016 partial offset); v7 ~nil.**
- h-B5-veteran-blowout-is-v7 (D4): **CONFIRMED as v7-asc specifically** (27/31 joiners).
- supervisor-expected-8-obituary-layers: **FALSIFIED — 9 rows** (JS legacy chain is the 9th, flagged).

## Burn / process
Engine loads this session: gate1 (1) + gates board (1) + measurement suite ×6 (head, candidate, m1off, cboff, ascoff, m2off) + matrix builds ×3 = **12, all sequential**. Matrix builds ~86s each (7147 builder). Canonical workspace restored + md5-verified (8aed420a / 346cffbb) after the variant block. Estimate ~3.0h posted; actual well under (builds far cheaper than sized) — no split, all five ASKs delivered.
