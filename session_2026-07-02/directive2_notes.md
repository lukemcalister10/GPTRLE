# DIRECTIVE 2 notes — 2026-07-02 — diagnostics + gate re-specs — head 8aed420a store 644d1254
_Zero engine/store edits. Scratch evaluations only (A/B/F). Gate-script + doc edits per Luke's rulings (02/07, turns 09-10)._

## TASK A — H-WARD isolation (M1+v7 prototype, SCRATCH) → H-WARD **FALSIFIED as the full explanation**
Four-player 2026 verdict (prototype = M1 + refined-v7 applied at inference in a scratch harness; at-head = board values):
| player | at-head 2026 | prototype 2026 | move |
|---|---|---|---|
| Josh Ward | 1782 | **1253** | −27% (v7 shaves the trend-up/level-flat riser) |
| Paul Curtis | 1162 | 1087 | −6% |
| Josh Weddle | 1628 | 1414 | −14% |
| Jack Ginnivan | 1578 | **1677** | +6% (M1 fires) |
- **A9 FLIPS** (Ginnivan 1677 > Ward 1253). **A2 flips only its Weddle leg** (1414 > 1253); **Curtis stays BELOW Ward**
  (1087 < 1253) because v7 also shaves Curtis — so A2 would remain RED under the prototype.
- **A5 clears everywhere**: Ginnivan 1677 (+77 over the 1600 floor), Bowey 2555 (+455 over 2100), Blakey 3424 (+824 over 2600).
- Verdict: the un-baked M1+v7 explains the Ginnivan-low half of the pattern and most of Ward-high, but NOT the
  Curtis<Ward residual → H-WARD moves to FALSIFIED (as sole cause); the residual Curtis-vs-Ward relativity is a
  separate open question (undecomposed — no cause label).
- Read-pass pack (2025 complete-season basis, 2026 column EXCLUDED): `readpass_pack_M1v7_8aed420a.md` (this dir).

## TASK B — B4-h1 isolation → **h1 NOT CONFIRMED on git-recoverable evidence**
- Git seed (f4a4d34) store identities: live = pre_stage0 = `644d1254`; stage0 = `91a3de6b`. No other store state exists in history.
- Regenerated board from the stage0 store (temporary swap in the runtime workspace, restored + verified `644d1254` after):
  md5 = `c16e1024` — matches NEITHER shipped `b8f9e998` NOR the reconciled-store regen `1898ead7`.
- Value-level diff, shipped vs reconciled-regen: **18/58 top-level blocks differ, structurally and large** —
  `SCALE` 6.53492→4.48537 (−31%), `intakePickSum` 97973→58403, `intakeFull` 109331→63947, `PVC` differs at all 99
  subkeys, `active`/`cohort` payloads differ by 10–40% in size. This is far beyond environment FP drift.
- Evidence now favors **h3** (the export-path/parameter state moved after the board was cut) over h2 (env-at-cut):
  env drift cannot move `SCALE` by 31% or halve the intake sums. Cause NOT labeled (per directive).
- **Proposed next isolation**: regenerate at the CANONICAL frozen engine (`backups/_merged_recover.py.e0ac9c37_CANONICAL`)
  × each of the three seed stores, byte-compare to `b8f9e998` — isolates the code axis with store + env pinned.

## TASK C — B5 offender list (shipped-B5 population; list status per the G3 convention — all 9 are LISTED, 0 delisted)
| player | pos | pick | drafted | ev | draftval | ratio | g25 | g26 | yrs | status |
|---|---|---|---|---|---|---|---|---|---|---|
| Jack Watkins | MID | 3 | 2025 | 18 | 308 | 0.06 | 0 | 9 | 1 | listed |
| Flynn Perez | GEN_DEF | 35 | 2025 | 39 | 308 | 0.13 | 0 | 5 | 1 | listed |
| Zac Banch | GEN_FWD | 2 | 2025 | 45 | 308 | 0.15 | 6 | 2 | 1 | listed |
| Flynn Young | GEN_FWD | 4 | 2025 | 46 | 308 | 0.15 | 12 | 3 | 1 | listed |
| Saad El-Hawli | GEN_DEF | 13 | 2024 | 50 | 308 | 0.16 | 9 | 7 | 2 | listed |
| Lachlan Blakiston | KEY_DEF | 13 | 2025 | 51 | 308 | 0.17 | 16 | 14 | 1 | listed |
| Jack Hutchinson | MID | 3 | 2024 | 56 | 308 | 0.18 | 16 | 2 | 2 | listed |
| Mani Liddy | MID | 16 | 2025 | 58 | 308 | 0.19 | 13 | 0 | 1 | listed |
| Roan Steele | MID | 8 | 2025 | 70 | 308 | 0.23 | 7 | 13 | 1 | listed |
No hypothesis, no fix (Luke classifies). Note: the listed-only population convention does not change this list (0 delisted).

## TASK D — the 9→10g dip, quantified (numbers only)
- Channel trace on the B6 synth (2025-draft MID pk10 avg85): `Lo` (par-shrunk level) rises smoothly 64.1→77.0 across
  1→14g; `Leff` tracks `Lo` exactly through 9g (72.1); **at 10g an evidence-onset overlay activates (`_eo`>0) and caps
  `Leff` at 68.6, where it stays frozen through 14g** while `Lo` keeps rising. ev: 3538 (9g) → 3318 (10g) = **−220**.
- Cohort variant grid (4 positions × picks 2/10/40 × avgs 65/85/105, 36 variants): **29/36 dip at 9→10g** and in those
  29 it is the worst dip anywhere in 6..14g; worst = **−601** (KEY_FWD pk40 avg105); KEY_FWD dips in 9/9 variants;
  the exceptions are pick-2 variants at avg 65/105. Second dip (13→14g) is −5 on the canonical synth.
- Monotonicity: **YES, violating** B6's more-games-never-worth-less clause — same 85.0 scoring rate, +1 game, −220
  (violations on the canonical synth: (9→10, −220), (13→14, −5)).

## TASK E — B2 noise floor (N=5 under pins)
See the N=5 table appended below (§E-results). Tolerance to be set by the supervisor (Luke has delegated);
5.0 %-pts stays provisional this run.

## TASK F — current-season-drop pin-mechanism (reissue of the 01/07 relay, re-stamped 02/07) → **H1 FALSIFIED**
Reproduced the 01/07 decomposition byte-for-byte at head 8aed420a / store 644d1254:
- Rozee (`connor-rozee`, 2g/80 in 2026): ev25 3874 → ev26 2679 (−31%) = **(a) age/tenure + prior-decay + exposure-feature
  −827 (−21%)** + (b) thin-2026 level pull −368 (−9%); counterfactual (no-2026-games) = 3047.
- `_lvl_wt` 2025=96.6 → 2026=96.0; the 2g 2026 gets **4%** of the recency-weighted level weight (g<6 population:
  mean 12%, median 9%) — the thin season is already size-discounted.
- Cross-cohort channel split (g<6-in-2026, n=62): d_level = **+5 / +1 / +5 %** (young/mid/old — uniform, tiny, POSITIVE);
  d_age = **−48 / −31 / −26 %** (cohort-VARYING, inverted vs aging). avg26−avg25: mean −4.7, median −1.4, 56% below.
- **H1 (`_lvl_wt` over-reacts to a thin below-par 2026 sample) is FALSIFIED**: the level channel is small for Rozee and
  slightly positive in every cohort; the dominant channel is the exposure-feature/recency-decay dynamics (cohort-varying,
  young ≫ old). No fix design in this directive (per instruction).

## TASK G — gate re-specs (ship_gates_check.py + docs only)
- **G1 (B1)** re-scripted: PASS = POOLED value rises from draft to a peak by yr4-5 (yr6 acceptable); interim pre-peak
  dips <5% tolerated (year 2 explicitly named); no yr6-hold required. Per-cohort rise-to-yr4-6 kept as backstop.
- **G2 (B6)** re-scripted to the WHOLE 0→6 ramp (0-game sit-out anchor → 6-game production value); flat-then-step IS the
  violation; monotone-in-evidence clause unchanged. DECLARED smoothness thresholds pending ratification: no single 0→6
  step > 50% of the total 0→6 rise; cumulative rise by 3g ≥ 25% of it. The superseded formula is echoed in the return.
- **G3 (B5)** population convention recorded (script + here): ACTIVE/LISTED only; once inactive, value = 0; in backtests
  inactive players REMAIN in denominators while contributing 0 to numerators for that year.
- **G4**: A6 kernel bw 0.6 on log-pick **RATIFIED** (via Luke's delegation to the supervisor, 02/07); B2 tol 5.0
  provisional pending Task E.

### G3 — by-year value/draftval distribution (LISTED players, n=696, at head) + crater-floor PROPOSAL (Luke signs)
Finest resolution = single years-in-system (yrs = 2026 − draft year); yr12+ pooled (n=93); smoothing = 3-yr centred
moving average on the percentile tracks (this is also the thin-year pooling; smallest single-year n = 33).
```
yrs :   1    2    3    4    5    6    7    8    9   10   11  12+
n   :  80   91   68   50   64   43   41   41   44   48   33   93
p5  : .16  .27  .25  .23  .19  .07  .08  .01  .01  .09  .02  .02
p10 : .48  .50  .25  .23  .20  .07  .10  .05  .03  .11  .04  .04
p50 : .50  .70  .73  .62 1.10  .53  .99  .73  .69  .77  .75  .65
smoothed p5 : .22 .23 .25 .22 .16 .11 .05 .04 .04 .04 .05 .02
```
**PROPOSAL (replaces the flat 0.25×; anchored to the smoothed p5 track): yr1-4 = 0.25×, yr5 = 0.15×, yr6 = 0.10×,
yr7+ = 0.05× draftval.** Rationale: smoothed p5 sits at 0.22-0.25 through yr4 (the flat floor is about right there),
then decays — a flat 0.25× would mislabel normal veteran value decay as cratering from yr5 on. B5 currently tests
yr1-2 only, where the schedule = 0.25× (no board effect); the schedule matters if/when the guard extends past yr2.
PROPOSAL ONLY — 0.25× stays provisional on the board this run.

## Hypothesis register (after this directive)
- **H-WARD** (A2/A9/A5 reds explained by un-baked M1+v7): **FALSIFIED as sole cause** — flips A9 + Weddle leg + clears
  A5 floors, but Curtis<Ward survives the prototype. Residual: Curtis-vs-Ward relativity, undecomposed.
- **B4 h1** (shipped board = pre-reconciliation live store): **NOT CONFIRMED** — no git-recoverable store reproduces
  `b8f9e998`. Evidence favors h3 over h2 (structural/large diffs, not env drift). Cause UNKNOWN, not labeled.
- **H1** (`_lvl_wt` over-reaction, current-season drop): **FALSIFIED** (Task F channel numbers).
- **NEW observation (no cause label)**: B6's 9→10g dip = evidence-onset overlay capping `Leff` at 10g (Task D trace).

## §E-results — B2 noise floor, N=5 under pins (2026-07-02, this container)
Five sequential `_gate1_wf.py` runs, identical pinned env. Metric tables byte-identical across all 5 runs
(output-file md5s differ ONLY on per-cohort wall-time lines, e.g. "17s" vs "18s"):
```
run 1..5 (identical): median|IS-WF| = 0.00 %-pts   max single gap = 3   mean gap = 0.47
separation (GOOD/BUST WF medians): GEN_DEF 52/1, GEN_FWD 44/1, KEY_DEF 60/1, KEY_FWD 64/1, MID 52/0
```
**Spread of the B2 leakage metric = 0.00 %-pts (N=5).** Under pins the metric is deterministic; the observed noise
floor is zero. Tolerance decision is the supervisor's (Luke delegated); 5.0 %-pts stays provisional this run.
